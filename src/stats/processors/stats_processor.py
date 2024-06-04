import polars as pl

from data.data_extract import get_processing_operation_codes_data
from data.data_processing import (
    create_icpe_installations_df,
    create_icpe_regional_df,
    get_mean_packagings_by_bsff,
    get_mean_quantity_by_bsff_packagings,
    get_recovered_and_eliminated_quantity_processed_by_week_series,
    get_summed_statistics,
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

from ..models import (
    Computation,
    DepartementsComputation,
    FranceComputation,
    InstallationsComputation,
    RegionsComputation,
)


def build_stats_and_figs(year: int, clear_year: bool = False):
    existing_computations = [
        Computation.objects.filter(year=year),
        DepartementsComputation.objects.filter(year=year),
        InstallationsComputation.objects.filter(year=year),
        RegionsComputation.objects.filter(year=year),
    ]
    if clear_year:
        for computation_o in existing_computations:
            computation_o.delete()

    date_interval = get_data_date_interval_for_year(year)

    bsdd_weekly_data_df = pl.read_parquet("temp_data/bsdd_weekly_data.parquet")
    bsda_weekly_data_df = pl.read_parquet("temp_data/bsda_weekly_data.parquet")
    bsff_weekly_data_df = pl.read_parquet("temp_data/bsff_weekly_data.parquet")
    bsdasri_weekly_data_df = pl.read_parquet("temp_data/bsdasri_weekly_data.parquet")
    bsvhu_weekly_data_df = pl.read_parquet("temp_data/bsvhu_weekly_data.parquet")
    bsd_non_dangerous_weekly_data_df = pl.read_parquet("temp_data/bsd_non_dangerous_weekly_data.parquet")
    accounts_weekly_data_df = pl.read_parquet("temp_data/accounts_weekly_data.parquet")
    weekly_waste_processed_data_df = pl.read_parquet("temp_data/weekly_waste_processed_data.parquet")
    accounts_by_naf_data_df = pl.read_parquet("temp_data/accounts_by_naf_data.parquet")
    waste_produced_by_naf_annual_stats_df = pl.read_parquet("temp_data/waste_produced_by_naf_annual_stats.parquet")
    icpe_installations_data = pl.read_parquet("temp_data/icpe_installations_data.parquet")
    icpe_installations_waste_processed_data = pl.read_parquet(
        "temp_data/icpe_installations_waste_processed_data.parquet"
    )
    icpe_departements_waste_processed_data = pl.read_parquet(
        "temp_data/icpe_departements_waste_processed_data.parquet"
    )
    icpe_regions_waste_processed_data = pl.read_parquet("temp_data/icpe_regions_waste_processed_data.parquet")
    icpe_france_waste_processed_data = pl.read_parquet("temp_data/icpe_france_waste_processed_data.parquet")

    bs_weekly_datasets = {
        "BSDD": bsdd_weekly_data_df,
        "BSDA": bsda_weekly_data_df,
        "BSFF": bsff_weekly_data_df,
        "BSDASRI": bsdasri_weekly_data_df,
        "BSVHU": bsvhu_weekly_data_df,
    }

    total_bs_created = get_total_bs_created(
        {**bs_weekly_datasets, "BS de déchets non dangereux": bsd_non_dangerous_weekly_data_df}
    )
    total_quantity_processed = get_total_quantity_processed(bs_weekly_datasets)
    total_quantity_processed_non_dangerous = get_summed_statistics(
        bsd_non_dangerous_weekly_data_df, "quantite_traitee_operations_finales"
    )
    total_companies_created = get_total_number_of_accounts_created(accounts_weekly_data_df, "comptes_etablissements")

    # BSx weekly figures
    bsdd_weekly_filtered_df = get_weekly_preprocessed_dfs(bsdd_weekly_data_df, date_interval)
    bsda_weekly_filtered_df = get_weekly_preprocessed_dfs(bsda_weekly_data_df, date_interval)
    bsff_weekly_filtered_df = get_weekly_preprocessed_dfs(bsff_weekly_data_df, date_interval)
    bsdasri_weekly_filtered_df = get_weekly_preprocessed_dfs(bsdasri_weekly_data_df, date_interval)
    bsvhu_weekly_filtered_df = get_weekly_preprocessed_dfs(bsvhu_weekly_data_df, date_interval)
    bsd_non_dangerous_weekly_filtered_df = get_weekly_preprocessed_dfs(bsd_non_dangerous_weekly_data_df, date_interval)

    bsdd_counts_weekly_fig = create_weekly_scatter_figure(
        bsdd_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSDD",
    )
    bsda_counts_weekly_fig = create_weekly_scatter_figure(
        bsda_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSDA",
    )
    bsff_counts_weekly_fig = create_weekly_scatter_figure(
        bsff_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSFF",
    )
    bsff_packagings_counts_weekly_fig = create_weekly_scatter_figure(
        bsff_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSFF PACKAGINGS",
    )
    bsdasri_counts_weekly_fig = create_weekly_scatter_figure(
        bsdasri_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSDASRI",
    )
    bsvhu_counts_weekly_fig = create_weekly_scatter_figure(
        bsvhu_weekly_filtered_df,
        metric_type="counts",
        bs_type="BSVHU",
    )
    bsd_non_dangerous_counts_weekly_fig = create_weekly_scatter_figure(
        bsd_non_dangerous_weekly_filtered_df, metric_type="counts", bs_type="BS de déchets non dangereux"
    )

    bsdd_quantities_weekly_fig = create_weekly_scatter_figure(
        bsdd_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSDD",
    )
    bsda_quantities_weekly_fig = create_weekly_scatter_figure(
        bsda_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSDA",
    )
    bsff_quantities_weekly_fig = create_weekly_scatter_figure(
        bsff_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSFF",
    )
    bsdasri_quantities_weekly_fig = create_weekly_scatter_figure(
        bsdasri_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSDASRI",
    )
    bsvhu_quantities_weekly_fig = create_weekly_scatter_figure(
        bsvhu_weekly_filtered_df,
        metric_type="quantity",
        bs_type="BSDASRI",
    )
    bsd_non_dangerous_quantities_weekly_fig = create_weekly_scatter_figure(
        bsd_non_dangerous_weekly_filtered_df, metric_type="quantity", bs_type="BS de déchets non dangereux"
    )

    # BSx weekly stats
    bsdd_bordereaux_created = get_summed_statistics(bsdd_weekly_filtered_df, "creations")
    bsda_bordereaux_created = get_summed_statistics(bsda_weekly_filtered_df, "creations")
    bsff_bordereaux_created = get_summed_statistics(bsff_weekly_filtered_df, "creations_bordereaux")
    bsdasri_bordereaux_created = get_summed_statistics(bsdasri_weekly_filtered_df, "creations")
    bsvhu_bordereaux_created = get_summed_statistics(bsvhu_weekly_filtered_df, "creations")
    bsd_non_dangerous_bordereaux_created = get_summed_statistics(bsd_non_dangerous_weekly_filtered_df, "creations")

    bsdd_quantity_processed = get_summed_statistics(bsdd_weekly_filtered_df, "quantite_traitee_operations_finales")
    bsda_quantity_processed = get_summed_statistics(bsda_weekly_filtered_df, "quantite_traitee_operations_finales")
    bsff_quantity_processed = get_summed_statistics(bsff_weekly_filtered_df, "quantite_traitee_operations_finales")
    bsdasri_quantity_processed = get_summed_statistics(
        bsdasri_weekly_filtered_df, "quantite_traitee_operations_finales"
    )
    bsvhu_quantity_processed = get_summed_statistics(bsvhu_weekly_filtered_df, "quantite_traitee_operations_finales")
    bsd_non_dangerous_quantity_processed = get_summed_statistics(
        bsd_non_dangerous_weekly_filtered_df, "quantite_traitee_operations_finales"
    )

    # BSFF specific stats
    mean_quantity_by_bsff_packagings = get_mean_quantity_by_bsff_packagings(bsff_weekly_filtered_df)
    mean_packagings_by_bsff = get_mean_packagings_by_bsff(bsff_weekly_filtered_df)

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
        bs_weekly_datasets,
        date_interval,
    )
    quantity_processed_non_dangerous_yearly = get_summed_statistics(
        bsd_non_dangerous_weekly_data_df, "quantite_traitee_operations_finales", date_interval
    )
    bs_created_yearly = get_total_bs_created(
        {**bs_weekly_datasets, "BS de déchets non dangereux": bsd_non_dangerous_weekly_data_df},
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
        waste_produced_by_naf_annual_stats_df, use_quantity=True, year=year
    )

    Computation.objects.create(
        year=year,
        total_bs_created=total_bs_created,
        total_quantity_processed=total_quantity_processed,
        total_quantity_processed_non_dangerous=total_quantity_processed_non_dangerous,
        total_companies_created=total_companies_created,
        quantity_processed_yearly=quantity_processed_yearly,
        quantity_processed_non_dangerous_yearly=quantity_processed_non_dangerous_yearly,
        bs_created_yearly=bs_created_yearly,
        quantity_processed_weekly=quantity_processed_weekly_fig.to_json(),
        quantity_processed_sunburst=quantity_processed_sunburst_fig.to_json(),
        bsdd_counts_weekly=bsdd_counts_weekly_fig.to_json(),
        bsda_counts_weekly=bsda_counts_weekly_fig.to_json(),
        bsff_counts_weekly=bsff_counts_weekly_fig.to_json(),
        bsff_packagings_counts_weekly=bsff_packagings_counts_weekly_fig.to_json(),
        bsdasri_counts_weekly=bsdasri_counts_weekly_fig.to_json(),
        bsvhu_counts_weekly=bsvhu_counts_weekly_fig.to_json(),
        bsd_non_dangerous_counts_weekly=bsd_non_dangerous_counts_weekly_fig.to_json(),
        bsdd_quantities_weekly=bsdd_quantities_weekly_fig.to_json(),
        bsda_quantities_weekly=bsda_quantities_weekly_fig.to_json(),
        bsff_quantities_weekly=bsff_quantities_weekly_fig.to_json(),
        bsdasri_quantities_weekly=bsdasri_quantities_weekly_fig.to_json(),
        bsvhu_quantities_weekly=bsvhu_quantities_weekly_fig.to_json(),
        bsd_non_dangerous_quantities_weekly=bsd_non_dangerous_quantities_weekly_fig.to_json(),
        bsdd_bordereaux_created=bsdd_bordereaux_created,
        bsda_bordereaux_created=bsda_bordereaux_created,
        bsff_bordereaux_created=bsff_bordereaux_created,
        bsdasri_bordereaux_created=bsdasri_bordereaux_created,
        bsvhu_bordereaux_created=bsvhu_bordereaux_created,
        bsd_non_dangerous_bordereaux_created=bsd_non_dangerous_bordereaux_created,
        bsdd_quantity_processed=bsdd_quantity_processed,
        bsda_quantity_processed=bsda_quantity_processed,
        bsff_quantity_processed=bsff_quantity_processed,
        bsdasri_quantity_processed=bsdasri_quantity_processed,
        bsvhu_quantity_processed=bsvhu_quantity_processed,
        bsd_non_dangerous_quantity_processed=bsd_non_dangerous_quantity_processed,
        mean_quantity_by_bsff_packagings=mean_quantity_by_bsff_packagings,
        mean_packagings_by_bsff=mean_packagings_by_bsff,
        produced_quantity_by_category=produced_quantity_by_category_fig.to_json(),
        company_created_total_life=company_created_total_life,
        user_created_total_life=user_created_total_life,
        company_created_weekly=company_created_weekly_fig.to_json(),
        user_created_weekly=user_created_weekly_fig.to_json(),
        company_counts_by_category=treemap_companies_figure.to_json(),
    )

    icpe_installations_data = create_icpe_installations_df(
        icpe_installations_data, icpe_installations_waste_processed_data, date_interval
    )
    InstallationsComputation.objects.bulk_create(
        InstallationsComputation(**e) for e in icpe_installations_data.iter_rows(named=True)
    )

    icpe_regions_data = create_icpe_regional_df(
        icpe_regions_waste_processed_data,
        "code_region_insee",
        date_interval,
    )
    RegionsComputation.objects.bulk_create(RegionsComputation(**e) for e in icpe_regions_data.iter_rows(named=True))

    icpe_departements_data = create_icpe_regional_df(
        icpe_departements_waste_processed_data,
        "code_departement_insee",
        date_interval,
    )
    DepartementsComputation.objects.bulk_create(
        DepartementsComputation(**e) for e in icpe_departements_data.iter_rows(named=True)
    )

    icpe_france_data = create_icpe_regional_df(
        icpe_france_waste_processed_data,
        None,
        date_interval,
    )
    FranceComputation.objects.bulk_create(FranceComputation(**e) for e in icpe_france_data.iter_rows(named=True))
