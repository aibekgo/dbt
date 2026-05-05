#!/usr/bin/env bash
# Pulls one image per lesson from docs.getdbt.com (dbt Labs' public docs site)
# into images/stageN/<lesson>/. Idempotent — re-running re-downloads only
# missing/empty files. Format below: lesson_dir|source_url|saved_filename|alt
set -euo pipefail

cd "$(dirname "$0")/.."

ok=0
fail=0
while IFS='|' read -r lesson url filename alt; do
  [ -z "${lesson:-}" ] && continue
  case "${lesson}" in \#*) continue ;; esac
  dest_dir="images/${lesson}"
  dest="${dest_dir}/${filename}"
  mkdir -p "${dest_dir}"
  if [ -s "${dest}" ]; then
    echo "  skip   ${dest}"
    ok=$((ok+1))
    continue
  fi
  if curl -fsSL --max-time 30 -o "${dest}" "${url}"; then
    echo "  ok     ${dest}"
    ok=$((ok+1))
  else
    echo "  FAIL   ${dest}  <-  ${url}"
    rm -f "${dest}"
    fail=$((fail+1))
  fi
done <<'EOF'
stage1/add_sources|https://docs.getdbt.com/img/docs/building-a-dbt-project/sources-dag.png|sources_dag.png|A small dbt project DAG with two source tables flowing into staging models
stage1/dbt_init|https://docs.getdbt.com/img/icons/dbt-core.svg|dbt_core_icon.svg|dbt Core icon — the open-source CLI you install with pip
stage1/project_yml|https://docs.getdbt.com/img/docs/building-a-dbt-project/dbt-explorer-exposures.png|dbt_explorer_project.png|A real dbt project visualized in dbt Explorer
stage2/dbt_build|https://docs.getdbt.com/img/docs/reference/indirect-selection-dbt-build.png|dbt_build_selection.png|How dbt build walks the DAG
stage2/dbt_docs|https://docs.getdbt.com/img/docs/collaborate/dbt-explorer/example-cll.png|dbt_docs_lineage.png|Auto-generated docs site showing column-level lineage
stage2/fact_model|https://docs.getdbt.com/img/docs/building-a-dbt-project/multihop-diagram.png|marts_multihop.png|Sources to staging to intermediate to marts
stage2/intermediate_model|https://docs.getdbt.com/img/docs/building-a-dbt-project/UDF-DAG.png|intermediate_dag.png|Intermediate models bridge staging to marts
stage2/more_staging|https://docs.getdbt.com/img/docs/building-a-dbt-project/sources-dag.png|sources_dag.png|Multiple sources, multiple staging models
stage2/multi_source_split|https://docs.getdbt.com/img/docs/building-a-dbt-project/sources-dag.png|multi_source_dag.png|Sources from different systems feeding their own staging branches
stage2/naming_conventions|https://docs.getdbt.com/img/docs/building-a-dbt-project/multihop-diagram.png|naming_layers.png|Folder layout mirrors the layer prefix
stage3/accepted_values_relationships|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|store_failures.gif|dbt test --store-failures writes failing rows to a table
stage3/analyses_intro|https://docs.getdbt.com/img/icons/dbt-bit.svg|dbt_bit_icon.svg|Analyses are SQL files dbt compiles but does not materialize
stage3/generic_tests|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|generic_tests.gif|Generic tests run against your models
stage3/seed_basics|https://docs.getdbt.com/img/icons/dbt-core.svg|seed_icon.svg|Seeds are CSV files dbt loads with dbt seed
stage3/singular_test|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|singular_test.gif|Singular tests pass when they return zero rows
stage3/tests_intro|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|tests_intro.gif|dbt tests run as SELECTs
stage4/ephemeral_model|https://docs.getdbt.com/img/docs/building-a-dbt-project/UDF-DAG.png|ephemeral_inline.png|Ephemeral models compile inline as CTEs
stage4/incremental_basic|https://docs.getdbt.com/img/docs/building-a-dbt-project/incremental-diagram.jpg|incremental_diagram.jpg|How incremental models append only new rows
stage4/incremental_merge|https://docs.getdbt.com/img/docs/building-a-dbt-project/microbatch/microbatch_filters.png|incremental_merge.png|Merge strategy deduplicates updates by unique_key
stage4/materialization_overview|https://docs.getdbt.com/img/docs/building-a-dbt-project/incremental-diagram.jpg|materializations.jpg|view, table, incremental, ephemeral
stage4/snapshot_scd2|https://docs.getdbt.com/img/docs/building-a-dbt-project/snapshot-freshness.png|snapshot_scd2.png|dbt snapshots: SCD Type 2 history of a slowly changing source
stage4/view_to_table|https://docs.getdbt.com/img/docs/building-a-dbt-project/incremental-diagram.jpg|view_to_table.jpg|Switching from view to table
stage5/dbt_utils_install|https://docs.getdbt.com/img/icons/dbt-bit.svg|dbt_utils_icon.svg|dbt_utils — the standard package
stage5/exposures|https://docs.getdbt.com/img/docs/building-a-dbt-project/dag-exposures.png|exposures_dag.png|Exposures hang downstream of your DAG
stage5/first_macro|https://docs.getdbt.com/img/docs/building-a-dbt-project/UDF-DAG.png|first_macro.png|Macros are reusable Jinja-templated SQL snippets
stage5/jinja_basics|https://docs.getdbt.com/img/docs/building-a-dbt-project/UDF-DAG.png|jinja_basics.png|Jinja drives dbt templating
stage5/state_selection|https://docs.getdbt.com/img/docs/reference/defer-diagram.png|state_defer.png|state:modified+ selects only what you changed
stage6/advanced_testing_overview|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|advanced_testing.gif|Beyond the four built-in tests
stage6/commands_tour|https://docs.getdbt.com/img/docs/reference/indirect-selection-eager.png|commands_tour.png|How dbt CLI selectors pick nodes
stage6/custom_generic_test|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|custom_test.gif|Roll your own generic test
stage6/dbt_expectations_install|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|dbt_expectations.gif|dbt-expectations: Great-Expectations for dbt
stage6/dbt_show_command|https://docs.getdbt.com/img/icons/command-line.svg|dbt_show_cli.svg|dbt show peeks at compiled output without materializing
stage6/severity_warn|https://docs.getdbt.com/img/docs/building-a-dbt-project/test-store-failures.gif|severity_warn.gif|Test severity: warn vs error
stage6/target_directory_tour|https://docs.getdbt.com/img/icons/dbt-core.svg|target_dir_icon.svg|target/ holds every artifact dbt drops on disk
stage7/analysis_to_model|https://docs.getdbt.com/img/docs/building-a-dbt-project/multihop-diagram.png|analysis_to_model.png|Promoting an analysis into a tested mart
stage7/course_complete|https://docs.getdbt.com/img/docs/platform-overview.jpg|platform_overview.jpg|The dbt platform end-to-end
stage7/deployment_patterns|https://docs.getdbt.com/img/docs/deploy/deploy-job-completion.jpg|deploy_job.jpg|A successful production run
stage7/multi_target_profile|https://docs.getdbt.com/img/docs/deploy/dbt-cloud-integrations.png|multi_target.png|Same project, multiple targets
stage7/tooling_landscape|https://docs.getdbt.com/img/docs/deploy/dbt-platform-integrations.png|tooling_landscape.png|Where dbt lives in the data tooling ecosystem
EOF

echo ""
echo "downloaded ok=${ok} fail=${fail}"
