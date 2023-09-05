import polars as pl

from data.data_extract import get_naf_nomenclature_data
from data.data_processing import (
    get_quantities_by_naf,
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_total_bs_created,
    get_total_quantity_processed,
    get_waste_quantity_processed_by_processing_code_df,
    get_weekly_aggregated_series,
    get_weekly_preprocessed_dfs,
    get_weekly_waste_quantity_processed_by_operation_code_df,
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


def build_figs(year, clear_year=False):
    existing_computations = Computation.objects.filter(year=year)
    if clear_year:
        existing_computations.delete()
    if existing_computations:
        return
    NAF_NOMENCLATURE_DATA = get_naf_nomenclature_data()

    date_interval = get_data_date_interval_for_year(year)
    # retrieve data
    all_bsd_data = pl.read_json("temp_data/all_bsds_data.json")
    company_data = pl.read_json("temp_data/company_data.json")
    user_data = pl.read_json("temp_data/user_data.json")
    bsdd_data_df = pl.read_json("temp_data/bsdd_data.json")
    bsda_data_df = pl.read_json("temp_data/bsda_data.json")
    bsff_data_df = pl.read_json("temp_data/bsff_data.json")
    bsdasri_data_df = pl.read_json("temp_data/bsdasri_data.json")

    total_bs_created = get_total_bs_created(all_bsd_data)
    total_quantity_processed = get_total_quantity_processed(all_bsd_data)
    total_companies_created = company_data.height

    # BSx weekly figures
    bsdd_weekly_processed_dfs = get_weekly_preprocessed_dfs(bsdd_data_df, date_interval)
    bsda_weekly_processed_dfs = get_weekly_preprocessed_dfs(bsda_data_df, date_interval)
    bsff_weekly_processed_dfs = get_weekly_preprocessed_dfs(bsff_data_df, date_interval)
    bsdasri_weekly_processed_dfs = get_weekly_preprocessed_dfs(bsdasri_data_df, date_interval)

    bsdd_counts_weekly_fig = create_weekly_scatter_figure(
        *bsdd_weekly_processed_dfs["counts"],
        bs_type="BSDD",
        lines_configs=lines_configs_count,
    )
    bsda_counts_weekly_fig = create_weekly_scatter_figure(
        *bsda_weekly_processed_dfs["counts"],
        bs_type="BSDA",
        lines_configs=lines_configs_count,
    )
    bsff_counts_weekly_fig = create_weekly_scatter_figure(
        *bsff_weekly_processed_dfs["counts"],
        bs_type="BSFF",
        lines_configs=lines_configs_count,
    )
    bsdasri_counts_weekly_fig = create_weekly_scatter_figure(
        *bsdasri_weekly_processed_dfs["counts"],
        bs_type="BSDASRI",
        lines_configs=lines_configs_count,
    )

    bsdd_quantities_weekly_fig = create_weekly_scatter_figure(
        *bsdd_weekly_processed_dfs["quantity"],
        bs_type="BSDD",
        lines_configs=lines_configs_quantities,
    )
    bsda_quantities_weekly_fig = create_weekly_scatter_figure(
        *bsda_weekly_processed_dfs["quantity"],
        bs_type="BSDA",
        lines_configs=lines_configs_quantities,
    )
    bsdasri_quantities_weekly_fig = create_weekly_scatter_figure(
        *bsdasri_weekly_processed_dfs["quantity"],
        bs_type="BSDASRI",
        lines_configs=lines_configs_quantities,
    )
    bsff_quantities_weekly_fig = create_weekly_scatter_figure(
        *bsdasri_weekly_processed_dfs["quantity"],
        bs_type="BSFF",
        lines_configs=lines_configs_quantities,
    )

    # Waste weight processed weekly
    quantity_processed_weekly_df = get_weekly_waste_quantity_processed_by_operation_code_df(
        all_bsd_data, date_interval
    )
    # Total bordereaux created

    # Waste weight processed weekly

    (
        recovered_quantity_series,
        eliminated_quantity_series,
    ) = get_recovered_and_eliminated_quantity_processed_by_week_series(quantity_processed_weekly_df)

    quantity_processed_weekly_fig = create_weekly_quantity_processed_figure(
        recovered_quantity_series, eliminated_quantity_series
    )
    waste_quantity_processed_by_processing_code_df = get_waste_quantity_processed_by_processing_code_df(
        quantity_processed_weekly_df
    )

    quantity_processed_sunburst_fig = create_quantity_processed_sunburst_figure(
        waste_quantity_processed_by_processing_code_df
    )

    quantity_processed_yearly = get_total_quantity_processed(all_bsd_data, date_interval)
    bs_created_yearly = get_total_bs_created(all_bsd_data, date_interval)
    # Company and user section
    company_data_df = company_data.filter(pl.col("created_at").is_between(*date_interval, closed="left"))
    user_data_df = user_data.filter(pl.col("created_at").is_between(*date_interval, closed="left"))

    company_created_total_life = company_data_df.height
    user_created_total_life = user_data_df.height

    company_created_weekly_df = get_weekly_aggregated_series(company_data_df)
    user_created_weekly_df = get_weekly_aggregated_series(user_data_df)

    company_created_weekly_fig = create_weekly_created_figure(company_created_weekly_df)
    user_created_weekly_fig = create_weekly_created_figure(user_created_weekly_df)

    treemap_companies_figure = create_treemap_companies_figure(company_data_df)
    all_bordereaux_with_naf = get_quantities_by_naf(all_bsd_data, NAF_NOMENCLATURE_DATA, date_interval)

    produced_quantity_by_category_fig = create_treemap_companies_figure(all_bordereaux_with_naf, use_quantity=True)
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
