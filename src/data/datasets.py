"""This module contains the raw datasets. 
The datasets are loaded in memory to be reusable by other functions.
"""
from dataclasses import dataclass

import polars as pl

from .data_extract import get_bs_data


@dataclass
class Computed:
    all_bsds_data: pl.DataFrame
    bsdd_data: pl.DataFrame
    bsdasri_data: pl.DataFrame
    bsff_data: pl.DataFrame
    bsda_data: pl.DataFrame


def get_data_df():
    BSDD_DATA = get_bs_data(
        "get_bsdd_data.sql",
    )
    BSDA_DATA = get_bs_data(
        "get_bsda_data.sql",
    )
    BSFF_DATA = get_bs_data(
        "get_bsff_data.sql",
    )
    BSDASRI_DATA = get_bs_data(
        "get_bsdasri_data.sql",
    )

    all_bsd_data = pl.concat([BSDD_DATA, BSDA_DATA, BSFF_DATA, BSDASRI_DATA], how="diagonal")
    data = Computed(
        all_bsds_data=all_bsd_data,
        bsdd_data=BSDD_DATA,
        bsdasri_data=BSDASRI_DATA,
        bsff_data=BSFF_DATA,
        bsda_data=BSDA_DATA,
    )
    return data
