"""This module contains the raw datasets. 
The datasets are loaded in memory to be reusable by other functions.
"""
from dataclasses import dataclass

import polars as pl

from data.queries import (
    accounts_by_naf_annual_stats_sql,
    accounts_weekly_stats_sql,
    bs_weekly_data_sql,
    waste_processed_by_naf_annual_stats_sql,
    weekly_waste_processed_stats_sql,
)

from .data_extract import extract_dataset, get_bs_data


@dataclass
class Computed:
    bsdd_weekly_data: pl.DataFrame
    bsda_weekly_data: pl.DataFrame
    bsff_weekly_data: pl.DataFrame
    bsdasri_weekly_data: pl.DataFrame
    bsvhu_weekly_data: pl.DataFrame

    accounts_weekly_data: pl.DataFrame

    weekly_waste_processed_data: pl.DataFrame

    accounts_by_naf_data: pl.DataFrame
    waste_processed_by_naf_annual_stats: pl.DataFrame


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

    accounts_weekly_data = extract_dataset(accounts_weekly_stats_sql)

    weekly_waste_processed_data = extract_dataset(weekly_waste_processed_stats_sql)

    accounts_by_naf_data = extract_dataset(accounts_by_naf_annual_stats_sql)
    waste_processed_by_naf_annual_stats = extract_dataset(waste_processed_by_naf_annual_stats_sql)

    data = Computed(
        bsdd_weekly_data=bsdd_weekly_data,
        bsda_weekly_data=bsda_weekly_data,
        bsff_weekly_data=bsff_weekly_data,
        bsdasri_weekly_data=bsdasri_weekly_data,
        bsvhu_weekly_data=bsvhu_weekly_data,
        accounts_weekly_data=accounts_weekly_data,
        weekly_waste_processed_data=weekly_waste_processed_data,
        accounts_by_naf_data=accounts_by_naf_data,
        waste_processed_by_naf_annual_stats=waste_processed_by_naf_annual_stats,
    )
    return data
