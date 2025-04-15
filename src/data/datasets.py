"""This module contains the raw datasets.
The datasets are loaded in memory to be reusable by other functions.
"""

from dataclasses import dataclass

import polars as pl

from data.queries import (
    accounts_by_naf_annual_stats_sql,
    accounts_weekly_stats_sql,
    bs_weekly_data_sql,
    icpe_departements_waste_processed_sql,
    icpe_france_waste_processed_sql,
    icpe_installations_sql,
    icpe_installations_waste_processed_sql,
    icpe_regions_waste_processed_sql,
    waste_produced_by_naf_annual_stats_sql,
    weekly_waste_processed_stats_sql,
)

from .data_extract import extract_dataset


@dataclass
class Computed:
    bsdd_weekly_data: pl.DataFrame
    bsda_weekly_data: pl.DataFrame
    bsff_weekly_data: pl.DataFrame
    bsdasri_weekly_data: pl.DataFrame
    bsvhu_weekly_data: pl.DataFrame
    bsd_non_dangerous_weekly_data: pl.DataFrame

    accounts_weekly_data: pl.DataFrame

    weekly_waste_processed_data: pl.DataFrame

    accounts_by_naf_data: pl.DataFrame
    waste_produced_by_naf_annual_stats: pl.DataFrame

    icpe_installations_data: pl.DataFrame
    icpe_installations_waste_processed_data: pl.DataFrame
    icpe_departements_waste_processed_data: pl.DataFrame
    icpe_regions_waste_processed_data: pl.DataFrame
    icpe_france_waste_processed_data: pl.DataFrame


def get_data_df():
    bsdd_weekly_data = extract_dataset(
        bs_weekly_data_sql.format("refined_zone_stats_publiques.bsdd_statistiques_hebdomadaires")
    )
    bsda_weekly_data = extract_dataset(
        bs_weekly_data_sql.format("refined_zone_stats_publiques.bsda_statistiques_hebdomadaires")
    )
    bsff_weekly_data = extract_dataset(
        bs_weekly_data_sql.format("refined_zone_stats_publiques.bsff_statistiques_hebdomadaires")
    )
    bsdasri_weekly_data = extract_dataset(
        bs_weekly_data_sql.format("refined_zone_stats_publiques.bsdasri_statistiques_hebdomadaires")
    )
    bsvhu_weekly_data = extract_dataset(
        bs_weekly_data_sql.format("refined_zone_stats_publiques.bsvhu_statistiques_hebdomadaires")
    )
    bsd_non_dangerous_weekly_data = extract_dataset(
        bs_weekly_data_sql.format("refined_zone_stats_publiques.bsd_non_dangereux_statistiques_hebdomadaires")
    )

    accounts_weekly_data = extract_dataset(accounts_weekly_stats_sql)

    weekly_waste_processed_data = extract_dataset(weekly_waste_processed_stats_sql)

    accounts_by_naf_data = extract_dataset(accounts_by_naf_annual_stats_sql)
    waste_produced_by_naf_annual_stats = extract_dataset(waste_produced_by_naf_annual_stats_sql)

    icpe_installations_data = extract_dataset(
        icpe_installations_sql,
        {
            "code_aiot": pl.String,
            "siret": pl.String,
            "raison_sociale": pl.String,
            "rubrique": pl.String,
            "quantite_autorisee": pl.Float64,
            "unite": pl.String,
            "latitude": pl.Float64,
            "longitude": pl.Float64,
            "adresse1": pl.String,
            "adresse2": pl.String,
            "code_postal": pl.String,
            "commune": pl.String,
        },
    )
    icpe_installations_waste_processed_data = extract_dataset(
        icpe_installations_waste_processed_sql,
        {
            "code_aiot": pl.String,
            "siret": pl.String,
            "raison_sociale": pl.String,
            "rubrique": pl.String,
            "quantite_autorisee": pl.Float64,
            "unite": pl.String,
            "latitude": pl.Float64,
            "longitude": pl.Float64,
            "adresse1": pl.String,
            "adresse2": pl.String,
            "code_postal": pl.String,
            "commune": pl.String,
        },
    )
    icpe_departements_waste_processed_data = extract_dataset(icpe_departements_waste_processed_sql)
    icpe_regions_waste_processed_data = extract_dataset(icpe_regions_waste_processed_sql)
    icpe_france_waste_processed_data = extract_dataset(icpe_france_waste_processed_sql)

    data = Computed(
        bsdd_weekly_data=bsdd_weekly_data,
        bsda_weekly_data=bsda_weekly_data,
        bsff_weekly_data=bsff_weekly_data,
        bsdasri_weekly_data=bsdasri_weekly_data,
        bsvhu_weekly_data=bsvhu_weekly_data,
        bsd_non_dangerous_weekly_data=bsd_non_dangerous_weekly_data,
        accounts_weekly_data=accounts_weekly_data,
        weekly_waste_processed_data=weekly_waste_processed_data,
        accounts_by_naf_data=accounts_by_naf_data,
        waste_produced_by_naf_annual_stats=waste_produced_by_naf_annual_stats,
        icpe_installations_data=icpe_installations_data,
        icpe_installations_waste_processed_data=icpe_installations_waste_processed_data,
        icpe_departements_waste_processed_data=icpe_departements_waste_processed_data,
        icpe_regions_waste_processed_data=icpe_regions_waste_processed_data,
        icpe_france_waste_processed_data=icpe_france_waste_processed_data,
    )
    return data
