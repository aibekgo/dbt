#!/usr/bin/env python3
"""Inserts a single image reference under the H1 of each target lesson .md.

Idempotent: if the lesson already references its image filename, this script
leaves it alone. Skips any lesson whose .md cannot be found.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mirror of fetch_lesson_images.sh — kept in sync by hand.
# tuple: (stage, lesson_id, filename, alt_text)
ENTRIES = [
    ("stage1", "add_sources", "sources_dag.png", "A small dbt project DAG with two source tables flowing into staging models"),
    ("stage1", "dbt_init", "dbt_core_icon.svg", "dbt Core — the open-source CLI you install with pip"),
    ("stage1", "project_yml", "dbt_explorer_project.png", "A real dbt project visualized in dbt Explorer"),
    ("stage2", "dbt_build", "dbt_build_selection.png", "How dbt build walks the DAG, running models, tests, snapshots, and seeds in dependency order"),
    ("stage2", "dbt_docs", "dbt_docs_lineage.png", "dbt's auto-generated docs site showing column-level lineage between models"),
    ("stage2", "fact_model", "marts_multihop.png", "Sources → staging → intermediate → marts: how dbt projects layer transformations"),
    ("stage2", "intermediate_model", "intermediate_dag.png", "Intermediate models as the connective tissue between staging and marts"),
    ("stage2", "more_staging", "sources_dag.png", "Multiple sources, multiple staging models — one per raw table"),
    ("stage2", "multi_source_split", "multi_source_dag.png", "Sources from different systems feeding their own staging branches"),
    ("stage2", "naming_conventions", "naming_layers.png", "Folder layout mirrors the layer prefix: stg__, int_, fct_, dim_"),
    ("stage3", "accepted_values_relationships", "store_failures.gif", "dbt test --store-failures writes failing rows to a table you can inspect"),
    ("stage3", "analyses_intro", "dbt_bit_icon.svg", "Analyses are SQL files dbt compiles but does not materialize"),
    ("stage3", "generic_tests", "generic_tests.gif", "Generic tests (unique, not_null, accepted_values, relationships) run against your models"),
    ("stage3", "seed_basics", "seed_icon.svg", "Seeds are CSV files dbt loads into the warehouse with dbt seed"),
    ("stage3", "singular_test", "singular_test.gif", "Singular tests are one-off SELECTs that pass when they return zero rows"),
    ("stage3", "tests_intro", "tests_intro.gif", "dbt tests run as SELECTs — any returned row is a failure"),
    ("stage4", "ephemeral_model", "ephemeral_inline.png", "Ephemeral models compile inline as CTEs into their downstream model"),
    ("stage4", "incremental_basic", "incremental_diagram.jpg", "How incremental models append only new rows after the first full run"),
    ("stage4", "incremental_merge", "incremental_merge.png", "Merge strategy: deduplicate updates by unique_key on each incremental run"),
    ("stage4", "materialization_overview", "materializations.jpg", "view, table, incremental, ephemeral — the four ways dbt materializes a model"),
    ("stage4", "snapshot_scd2", "snapshot_scd2.png", "dbt snapshots: SCD Type 2 history of a slowly changing source table"),
    ("stage4", "view_to_table", "view_to_table.jpg", "Switching a model from view to table: same SQL, different cost-and-speed tradeoff"),
    ("stage5", "dbt_utils_install", "dbt_utils_icon.svg", "dbt_utils — the standard package every dbt project ends up installing"),
    ("stage5", "exposures", "exposures_dag.png", "Exposures hang downstream of your DAG — dashboards, reports, ML models"),
    ("stage5", "first_macro", "first_macro.png", "Macros are reusable Jinja-templated SQL snippets, called like functions"),
    ("stage5", "jinja_basics", "jinja_basics.png", "Jinja drives dbt's templating — refs, sources, macros, control flow"),
    ("stage5", "state_selection", "state_defer.png", "state:modified+ selects only models you changed plus their downstream dependents"),
    ("stage6", "advanced_testing_overview", "advanced_testing.gif", "Beyond the four built-in tests: severity, custom generics, and packaged tests"),
    ("stage6", "commands_tour", "commands_tour.png", "The dbt CLI selector graph — dbt run, dbt test, dbt build and how they pick nodes"),
    ("stage6", "custom_generic_test", "custom_test.gif", "Roll your own generic test — declare it once, apply it via YAML"),
    ("stage6", "dbt_expectations_install", "dbt_expectations.gif", "dbt-expectations: Great-Expectations-flavored tests, packaged for dbt"),
    ("stage6", "dbt_show_command", "dbt_show_cli.svg", "dbt show --select model — peek at compiled output without materializing"),
    ("stage6", "severity_warn", "severity_warn.gif", "Test severity: warn for soft failures, error to break the build"),
    ("stage6", "target_directory_tour", "target_dir_icon.svg", "target/ — manifest.json, run_results.json, compiled SQL: every artifact dbt drops on disk"),
    ("stage7", "analysis_to_model", "analysis_to_model.png", "Promoting a one-off analysis into a tested, governed mart model"),
    ("stage7", "course_complete", "platform_overview.jpg", "The dbt platform end-to-end: develop, test, deploy, and discover"),
    ("stage7", "deployment_patterns", "deploy_job.jpg", "A successful production run in dbt Cloud — every model green"),
    ("stage7", "multi_target_profile", "multi_target.png", "Same project, multiple targets — dev/staging/prod from one profile"),
    ("stage7", "tooling_landscape", "tooling_landscape.png", "Where dbt lives in the broader data tooling ecosystem"),
]


def insert_image(md_path: Path, rel_image: str, alt: str) -> str:
    """Return the new md content. Inserts an image right after the H1 line.
    No-op if the image filename already appears in the file.
    """
    text = md_path.read_text()
    if rel_image in text:
        return text  # already wired up
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and line.lstrip().startswith("# "):
            # ensure a blank line, then the image, then a blank line
            if not (out and out[-1].endswith("\n")):
                out[-1] = out[-1] + "\n"
            out.append("\n")
            out.append(f"![{alt}]({rel_image})\n")
            inserted = True
    if not inserted:
        # no H1 found — prepend at top
        out = [f"![{alt}]({rel_image})\n", "\n"] + out
    return "".join(out)


def main() -> int:
    changed = 0
    skipped = 0
    missing = 0
    for stage, lesson, filename, alt in ENTRIES:
        md_path = ROOT / "lessons" / stage / f"{lesson}.md"
        if not md_path.exists():
            print(f"  MISSING md: {md_path.relative_to(ROOT)}")
            missing += 1
            continue
        rel_image = f"../../images/{stage}/{lesson}/{filename}"
        before = md_path.read_text()
        after = insert_image(md_path, rel_image, alt)
        if before == after:
            print(f"  skip   {md_path.relative_to(ROOT)} (already has image)")
            skipped += 1
        else:
            md_path.write_text(after)
            print(f"  ok     {md_path.relative_to(ROOT)}")
            changed += 1
    print()
    print(f"changed={changed} skipped={skipped} missing={missing}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
