import polars as pl
from data.data_extract import get_processing_operation_codes_data

from data.data_processing import (
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_total_bs_created,
    get_total_number_of_accounts_created,
    get_total_quantity_processed,
    get_weekly_preprocessed_dfs,
)
from data.figures_factory import (
    create_quantity_processed_sunburst_figure,
    create_treemap_companies_figure,
    create_weekly_created_figure,
    create_weekly_quantity_processed_figure,
    create_weekly_scatter_figure,
)
from data.utils import get_data_date_interval_for_year

from ..models import Computation

lines_configs_count = [
    {
        "name": "État initial",
        "suffix": "traçés",
        "text_position": "top center",
    },
    {
        "name": "Pris en charge par le transporteur",
        "suffix": "pris en charge par le transporteur",
        "text_position": "middle top",
    },
    {
        "name": "Reçu par le destinataire",
        "suffix": "reçus par le destinataire",
        "text_position": "middle bottom",
    },
    {
        "name": "Traité",
        "suffix": "marqués comme traités",
        "text_position": "bottom center",
    },
    {
        "name": "Traité (traitement intermédiaire)",
        "suffix": "en traitement intermédiaire",
        "text_position": "bottom center",
    },
    {
        "name": "Traité (traitement final)",
        "suffix": "en traitement final",
        "text_position": "bottom center",
    },
]

lines_configs_quantities = [
    {
        "name": "Quantité initiale",
        "suffix": "tonnes tracées",
        "text_position": "top center",
    },
    {
        "name": "Prise en charge par le transporteur",
        "suffix": "tonnes prises en charge par le transporteur",
        "text_position": "middle top",
    },
    {
        "name": "Reçue par le destinataire",
        "suffix": "tonnes reçues par le destinataire",
        "text_position": "middle bottom",
    },
    {
        "name": "Traitée",
        "suffix": "tonnes traitées",
        "text_position": "bottom center",
    },
    {
        "name": "Traitée (traitement intermédiaire)",
        "suffix": "tonnes traitées en traitement intermédiaire",
        "text_position": "bottom center",
    },
    {
        "name": "Traitée (traitement final)",
        "suffix": "tonnes traitées en traitement final",
        "text_position": "bottom center",
    },
]


def build_figs(year: int, clear_year: bool = False):
    existing_computations = Computation.objects.filter(year=year)
    if clear_year:
        existing_computations.delete()

    date_interval = get_data_date_interval_for_year(year)

    bsdd_weekly_data_df = pl.read_parquet("temp_data/bsdd_weekly_data.parquet")
    bsda_weekly_data_df = pl.read_parquet("temp_data/bsda_weekly_data.parquet")
    bsff_weekly_data_df = pl.read_parquet("temp_data/bsff_weekly_data.parquet")
    bsdasri_weekly_data_df = pl.read_parquet("temp_data/bsdasri_weekly_data.parquet")
    bsvhu_weekly_data_df = pl.read_parquet("temp_data/bsvhu_weekly_data.parquet")
    accounts_weekly_data_df = pl.read_parquet("temp_data/accounts_weekly_data.parquet")
    weekly_waste_processed_data_df = pl.read_parquet("temp_data/weekly_waste_processed_data.parquet")
    accounts_by_naf_data_df = pl.read_parquet("temp_data/accounts_by_naf_data.parquet")
    waste_processed_by_naf_annual_stats_df = pl.read_parquet("temp_data/waste_processed_by_naf_annual_stats.parquet")

    total_bs_created = get_total_bs_created(
        [bsdd_weekly_data_df, bsda_weekly_data_df, bsff_weekly_data_df, bsdasri_weekly_data_df, bsvhu_weekly_data_df]
    )
    total_quantity_processed = get_total_quantity_processed(
        [bsdd_weekly_data_df, bsda_weekly_data_df, bsff_weekly_data_df, bsdasri_weekly_data_df, bsvhu_weekly_data_df]
    )
    total_companies_created = get_total_number_of_accounts_created(accounts_weekly_data_df, "comptes_etablissements")

    # BSx weekly figures
    bsdd_weekly_filtered_df = get_weekly_preprocessed_dfs(bsdd_weekly_data_df, date_interval)
    bsda_weekly_filtered_df = get_weekly_preprocessed_dfs(bsda_weekly_data_df, date_interval)
    bsff_weekly_filtered_df = get_weekly_preprocessed_dfs(bsff_weekly_data_df, date_interval)
    bsdasri_weekly_filtered_df = get_weekly_preprocessed_dfs(bsdasri_weekly_data_df, date_interval)

    bsdd_counts_weekly_fig = create_weekly_scatter_figure(
        bsdd_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSDD",
        lines_configs=lines_configs_count,
    )
    bsda_counts_weekly_fig = create_weekly_scatter_figure(
        bsda_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSDA",
        lines_configs=lines_configs_count,
    )
    bsff_counts_weekly_fig = create_weekly_scatter_figure(
        bsff_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSFF",
        lines_configs=lines_configs_count,
    )
    bsdasri_counts_weekly_fig = create_weekly_scatter_figure(
        bsdasri_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSDASRI",
        lines_configs=lines_configs_count,
    )

    bsdd_quantities_weekly_fig = create_weekly_scatter_figure(
        bsdd_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSDD",
        lines_configs=lines_configs_quantities,
    )
    bsda_quantities_weekly_fig = create_weekly_scatter_figure(
        bsda_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSDA",
        lines_configs=lines_configs_quantities,
    )
    bsdasri_quantities_weekly_fig = create_weekly_scatter_figure(
        bsff_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSFF",
        lines_configs=lines_configs_quantities,
    )
    bsff_quantities_weekly_fig = create_weekly_scatter_figure(
        bsdasri_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSDASRI",
        lines_configs=lines_configs_quantities,
    )

    # Waste weight processed weekly

    (
        recovered_quantity_series,
        eliminated_quantity_series,
    ) = get_recovered_and_eliminated_quantity_processed_by_week_series(weekly_waste_processed_data_df)

    quantity_processed_weekly_fig = create_weekly_quantity_processed_figure(
        recovered_quantity_series, eliminated_quantity_series, date_interval
    )

    waste_codes_data = get_processing_operation_codes_data()
    quantity_processed_sunburst_fig = create_quantity_processed_sunburst_figure(
        weekly_waste_processed_data_df, waste_codes_data, date_interval
    )

    quantity_processed_yearly = get_total_quantity_processed(
        [bsdd_weekly_data_df, bsda_weekly_data_df, bsff_weekly_data_df, bsdasri_weekly_data_df, bsvhu_weekly_data_df],
        date_interval,
    )
    bs_created_yearly = get_total_bs_created(
        [bsdd_weekly_data_df, bsda_weekly_data_df, bsff_weekly_data_df, bsdasri_weekly_data_df, bsvhu_weekly_data_df],
        date_interval,
    )

    company_created_total_life = get_total_number_of_accounts_created(
        accounts_weekly_data_df, "comptes_etablissements", date_interval=date_interval
    )
    user_created_total_life = get_total_number_of_accounts_created(
        accounts_weekly_data_df, "comptes_utilisateurs", date_interval=date_interval
    )

    accounts_created_weekly_df = get_weekly_preprocessed_dfs(accounts_weekly_data_df, date_interval=date_interval)

    company_created_weekly_fig = create_weekly_created_figure(accounts_created_weekly_df, "comptes_etablissements")
    user_created_weekly_fig = create_weekly_created_figure(accounts_created_weekly_df, "comptes_utilisateurs")

    treemap_companies_figure = create_treemap_companies_figure(accounts_by_naf_data_df, year=year)

    produced_quantity_by_category_fig = create_treemap_companies_figure(
        waste_processed_by_naf_annual_stats_df, use_quantity=True, year=year
    )
    Computation.objects.create(
        year=year,
        total_bs_created=total_bs_created,
        total_quantity_processed=total_quantity_processed,
        total_companies_created=total_companies_created,
        quantity_processed_yearly=quantity_processed_yearly,
        bs_created_yearly=bs_created_yearly,
        quantity_processed_weekly=quantity_processed_weekly_fig.to_json(),
        quantity_processed_sunburst=quantity_processed_sunburst_fig.to_json(),
        bsdd_counts_weekly=bsdd_counts_weekly_fig.to_json(),
        bsda_counts_weekly=bsda_counts_weekly_fig.to_json(),
        bsff_counts_weekly=bsff_counts_weekly_fig.to_json(),
        bsdasri_counts_weekly=bsdasri_counts_weekly_fig.to_json(),
        bsdd_quantities_weekly=bsdd_quantities_weekly_fig.to_json(),
        bsda_quantities_weekly=bsda_quantities_weekly_fig.to_json(),
        bsff_quantities_weekly=bsff_quantities_weekly_fig.to_json(),
        bsdasri_quantities_weekly=bsdasri_quantities_weekly_fig.to_json(),
        produced_quantity_by_category=produced_quantity_by_category_fig.to_json(),
        company_created_total_life=company_created_total_life,
        user_created_total_life=user_created_total_life,
        company_created_weekly=company_created_weekly_fig.to_json(),
        user_created_weekly=user_created_weekly_fig.to_json(),
        company_counts_by_category=treemap_companies_figure.to_json(),
    )
