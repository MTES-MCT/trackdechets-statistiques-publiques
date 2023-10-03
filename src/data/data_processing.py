"""
Data gathering and processing
"""
from datetime import datetime
from typing import Tuple

import polars as pl


def get_weekly_preprocessed_dfs(
    bs_data: pl.DataFrame, date_interval: tuple[datetime, datetime] | None
) -> pl.DataFrame:
    """Preprocess raw 'bordereau' data in order to get data for the given date interval.

    Parameters
    ----------
    bs_data: DataFrame
        DataFrame containing raw 'bordereau' data.
    date_interval: tuple of two datetime objects
        Interval of date used to filter the data as datetime objects.
        First element is the start interval, the second one is the end of the interval.
        The interval is left inclusive.

    Returns
    -------
    DataFrame

    """

    bs_data_filtered = bs_data.filter(pl.col("semaine").is_between(*date_interval, closed="left")).sort("semaine")

    return bs_data_filtered


def get_recovered_and_eliminated_quantity_processed_by_week_series(
    weekly_waste_processed_data_df: pl.DataFrame,
) -> list[pl.Series]:
    """Extract the weekly quantity of recovered waste and eliminated waste in two separate Series.

    Parameters
    ----------
    quantity_processed_weekly_df: DataFrame
        DataFrame containing total weight of dangerous waste processed by week and by processing operation codes.

    Returns
    -------
    list of two series
        First element is the Series containing the weekly quantity of recovered waste
        and the second one the weekly quantity of eliminated waste.
    """

    series = weekly_waste_processed_data_df.groupby(["semaine", "type_operation"], maintain_order=True).agg(
        pl.col("quantite_traitee").sum()
    )

    res = [
        series.filter(pl.col("type_operation") == "Déchet valorisé"),
        series.filter(pl.col("type_operation") == "Déchet éliminé"),
    ]

    return res


def get_total_bs_created(
    all_bordereaux_data: list[pl.DataFrame],
    date_interval: Tuple[datetime, datetime] | None = None,
) -> int:
    """Returns the total number of 'bordereaux' created.

    Parameters
    ----------
    all_bordereaux_data: DataFrame
        Bordereaux data.
    date_interval: Tuple[datetime, datetime] | None
        Optional, datetime interval as tuple (left inclusive) to filter 'bordereaux' data.

    Returns
    -------
    int
        Total number of 'bordereaux' created.

    """
    bs_created_total = 0
    for df in all_bordereaux_data:
        if date_interval is not None:
            bs_created_total += (
                df.filter(pl.col("semaine").is_between(*date_interval, closed="left")).select("creations").sum().item()
            )
        else:
            bs_created_total += df.select("creations").sum().item()

    return bs_created_total


def get_total_quantity_processed(
    all_bordereaux_data: list[pl.DataFrame],
    date_interval: Tuple[datetime, datetime] | None = None,
) -> int:
    """Returns the total quantity processed (only final processing operation codes).

    Parameters
    ----------
    all_bordereaux_data: DataFrame
        Bordereaux data.
    date_interval: Tuple[datetime, datetime] | None
        Optional, datetime interval as tuple (left inclusive) to filter 'bordereaux' data.

    Returns
    -------
    float
        Total quantity processed.

    """
    quantity_processed_total = 0
    for df in all_bordereaux_data:
        if date_interval is not None:
            quantity_processed_total += (
                df.filter(pl.col("semaine").is_between(*date_interval, closed="left"))
                .select("quantite_traitee_operations_finales")
                .sum()
                .item()
            )
        else:
            quantity_processed_total += df.select("quantite_traitee_operations_finales").sum().item()

    return int(quantity_processed_total)


def get_total_number_of_accounts_created(
    accounts_data_df: pl.DataFrame,
    stats_column: str,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> pl.DataFrame:
    if date_interval is not None:
        accounts_data_df = accounts_data_df.filter(pl.col("semaine").is_between(*date_interval, closed="left"))

    number_of_accounts_created = accounts_data_df.select(stats_column).sum().item()

    return number_of_accounts_created
