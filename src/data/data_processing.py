"""
Data gathering and processing
"""

from datetime import datetime
from typing import Tuple

import polars as pl

from .figures_factory import create_icpe_graph


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


def get_summed_statistics(
    bordereaux_data: pl.DataFrame,
    stat_column: str,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> int:
    """
    Calculate the sum of a statistic in a specific date interval or for all dates.
    The `stat_column` parameter is used to select appropriate statistic column in the DataFrame (e.g. "creations","traitements"...)

    Parameters
    ----------
    bordereaux_data : pl.DataFrame
        DataFrame containing the data for a particular "bordereau" type.
    stat_column : str
        The column name that holds the statistical information.
    date_interval : Tuple[datetime, datetime], optional
        A tuple of two datetime objects representing the start and end of
        the desired time interval, by default None

    Returns
    -------
    int
        Number of bordereaux created in the given dataframe within specified
        date interval.

    Example
    -------
    >>> df = pl.DataFrame({"semaine": ["2021-01-01", "2021-02-01", "2021-02-05"],
                          "creations": [3, 7, 9]})
    >>> get_num_bordereaux_created(df, "creations", (datetime(2021,1,1), datetime(2021,2,2)))
        10
    """
    if len(bordereaux_data) == 0:
        return 0

    if date_interval is not None:
        summed = (
            bordereaux_data.filter(pl.col("semaine").is_between(*date_interval, closed="left"))
            .select(stat_column)
            .sum()
            .item()
        )
    else:
        summed = bordereaux_data.select(stat_column).sum().item()

    return summed


def get_total_bs_created(
    all_bordereaux_data: dict[str, pl.DataFrame],
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
    for bs_type, df in all_bordereaux_data.items():
        stat_column = "creations"
        if bs_type == "BSFF":
            stat_column = "creations_bordereaux"

        bs_created_total += get_summed_statistics(df, stat_column, date_interval)

    return bs_created_total


def get_total_quantity_processed(
    all_bordereaux_data: dict[str, pl.DataFrame],
    date_interval: Tuple[datetime, datetime] | None = None,
) -> int:
    """Returns the total quantity processed (only final processing operation codes).
    The quantity is casted down to an integer.

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
    for _, df in all_bordereaux_data.items():
        quantity_processed_total += get_summed_statistics(df, "quantite_traitee_operations_finales", date_interval)

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


def create_icpe_installations_df(
    df_installations: pl.DataFrame,
    df_installations_waste_processed: pl.DataFrame,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> pl.DataFrame:
    df_list = []
    for rubrique in ["2790", "2760-1", "2770"]:
        df_installations_filtered = df_installations.filter(pl.col("rubrique") == rubrique)

        df_installations_filtered = df_installations_filtered.group_by("code_aiot").agg(
            pl.col("siret").max(),
            pl.when(pl.col("quantite_autorisee").is_null().all())
            .then(None)
            .otherwise(pl.col("quantite_autorisee").sum())
            .alias("quantite_autorisee"),
            pl.col("latitude").max(),
            pl.col("longitude").max(),
            pl.col("raison_sociale").max(),
            pl.col("unite").max(),
            pl.col("adresse1").max(),
            pl.col("adresse2").max(),
            pl.col("code_postal").max(),
            pl.col("commune").max(),
        )

        df_waste_processed_filtered = df_installations_waste_processed.filter(
            (pl.col("rubrique") == rubrique) & (pl.col("day_of_processing").is_between(*date_interval, closed="left"))
        )

        agg_expr = pl.col("quantite_traitee").sum().alias("cumul_quantite_traitee").fill_null(0)
        metric_expr = (pl.col("cumul_quantite_traitee") / pl.col("quantite_autorisee")).alias("taux_consommation")
        if rubrique in ["2790", "2770"]:
            agg_expr = pl.col("quantite_traitee").mean().alias("moyenne_quantite_journaliere_traitee").fill_null(0)
            metric_expr = (pl.col("moyenne_quantite_journaliere_traitee") / pl.col("quantite_autorisee")).alias(
                "taux_consommation"
            )

        df_stats = df_waste_processed_filtered.group_by("code_aiot").agg(agg_expr)

        df_graphs = (
            df_waste_processed_filtered.filter(pl.col("day_of_processing").is_not_null())
            .sort(pl.col("day_of_processing"))
            .group_by("code_aiot")
            .map_groups(lambda x: create_icpe_graph(x, "code_aiot", rubrique))
        )

        df_installations_final = df_installations_filtered.join(
            df_stats, on="code_aiot", how="left", validate="1:1"
        ).join(df_graphs, on="code_aiot", how="left", validate="1:1")

        df_installations_final = df_installations_final.with_columns(
            pl.lit(rubrique).alias("rubrique"), pl.lit(date_interval[0].year).alias("year"), metric_expr
        )

        df_list.append(df_installations_final)

    gdf_final = pl.concat(df_list, how="diagonal")
    return gdf_final


def create_icpe_regional_df(
    df_regional_waste_processed: pl.DataFrame,
    regional_key_column: str | None = None,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> pl.DataFrame:
    """
    Function to create regional DataFrame for ICPE.
    The DataFrame is aggregated as regional level ("region" or "departement") if `regional_key_column` is provided.
    If `regional_key_column` is None, then the dataframe is computed for all of France;

    Parameters
    ----------
    df_regional_waste_processed : polars.DataFrame
        The DataFrame containing regional waste processed data.
    regional_key_column : str or None, optional
        The column name to be used as the key for regional grouping. If None, no grouping is performed (country-wide processing).
    date_interval : tuple or None, optional
        The date interval for filtering data. If None, no filtering is performed.

    Returns
    -------
    polars.DataFrame
        The DataFrame after processing with additional columns for mean daily waste processed,
        rate of consumption, authorized quantity, number of installations and plotly graph.
    """
    df_list = []
    for rubrique in ["2790", "2760-1", "2770"]:
        df_waste_processed_filtered = df_regional_waste_processed.filter(
            (pl.col("rubrique") == rubrique)
            & (
                pl.col("day_of_processing").is_between(*date_interval, closed="left")
                | pl.col("day_of_processing").is_null()
            )
        )

        if regional_key_column is not None:
            df_waste_processed_filtered = df_waste_processed_filtered.with_columns(
                pl.col(regional_key_column).cast(pl.String)
            )

        # Add annual stats and authorized quantity by departement/region
        agg_expr = pl.col("quantite_traitee").mean().alias("moyenne_quantite_journaliere_traitee").fill_null(0)
        metric_expr = (pl.col("moyenne_quantite_journaliere_traitee") / pl.col("quantite_autorisee")).alias(
            "taux_consommation"
        )
        if rubrique == "2760-1":
            agg_expr = pl.col("quantite_traitee").sum().alias("cumul_quantite_traitee").fill_null(0)
            metric_expr = (pl.col("cumul_quantite_traitee") / pl.col("quantite_autorisee")).alias("taux_consommation")

        agg_exprs = [agg_expr, pl.col("quantite_autorisee").max(), pl.col("nombre_installations").max()]

        if regional_key_column is None:
            annual_stats = df_waste_processed_filtered.groupby("rubrique").agg(*agg_exprs)
            annual_stats = annual_stats.with_columns(metric_expr)
            df = annual_stats
            df = df.with_columns(
                pl.lit(create_icpe_graph(df_waste_processed_filtered, key_column=None, rubrique=rubrique)).alias(
                    "graph"
                ),
                pl.lit(rubrique).alias("rubrique"),
                pl.lit(date_interval[0].year).alias("year"),
            )
        else:
            layer_name = "nom_departement"
            if regional_key_column == "code_region_insee":
                layer_name = "nom_region"

            agg_exprs.append(pl.col(layer_name).max())
            annual_stats = (
                df_waste_processed_filtered.group_by(regional_key_column).agg(agg_exprs).with_columns(metric_expr)
            )

            # Create plotly graphs adding to daily waste processed the authorized quantity for each departement/region
            df_graphs = (
                df_waste_processed_filtered.filter(pl.col("day_of_processing").is_not_null())
                .sort(pl.col("day_of_processing"))
                .group_by(regional_key_column)
                .map_groups(lambda x: create_icpe_graph(x, key_column=regional_key_column, rubrique=rubrique))
            )

            df = annual_stats.join(df_graphs, on=regional_key_column, how="outer_coalesce", validate="1:1")
            df = df.with_columns(pl.lit(rubrique).alias("rubrique"), pl.lit(date_interval[0].year).alias("year"))
        df_list.append(df)

    df_concat = pl.concat(df_list, how="diagonal")

    if regional_key_column:
        df_concat = df_concat.filter(pl.col(regional_key_column).is_not_null())

    return df_concat


def get_mean_quantity_by_bsff_packagings(bsff_data: pl.DataFrame) -> float:
    """
    Compute the mean waste quantity by BSFF packagings.

    Parameters:
    -----------
    bsff_data : pl.DataFrame
        Input data frame containing BSFF information.

    Returns:
    --------
    mean_quantity_by_packaging : float
        Mean quantity by BSFF packagings (converted into kilograms).

    Example:
    --------
    >>> df = pl.DataFrame({"semaine": ["2022-01-01", "2022-01-05"],
                           "quantite_traitee_operations_finales": [10, 15],
                           "traitements_contenants_operations_finales": [5, 7]})
    >>> get_mean_quantity_by_bsff_packagings(df, date_interval)
    Out: 2071
    """

    mean_quantity_by_packaging = None

    if len(bsff_data) > 0:
        mean_quantity_by_packaging = round(
            bsff_data.select(
                pl.col("quantite_traitee_operations_finales").sum()
                / pl.col("traitements_contenants_operations_finales").sum()
            ).item()
            * 1000,
            2,
        )

    return mean_quantity_by_packaging


def get_mean_packagings_by_bsff(bsff_data: pl.DataFrame) -> float:
    """
    Calculate and return the mean number of packagings per BSFF.

    Parameters:
    --------
    bsff_data : pl.DataFrame
        Input DataFrame containing the BSFF data with columns like 'semaine',
        'traitements_contenants' and 'traitements_bordereaux'.

    Returns:
    --------
    float
        Mean number of packagings per BSFF.

    Examples:
    >>> bsff_data = pl.DataFrame({'semaine': ['2022-01-01', '2022-01-02'],
                                  'traitements_contenants': [5, 6],
                                  'traitements_bordereaux': [3, 4]})
    >>> get_mean_packagings_by_bsff(bsff_data)
    Out: 1.5833333333
    """
    mean_packagings_by_bssf = None
    if len(bsff_data) > 0:
        mean_packagings_by_bssf = round(
            bsff_data.select((pl.col("traitements_contenants") / pl.col("traitements_bordereaux")).mean()).item(), 2
        )

    return mean_packagings_by_bssf
