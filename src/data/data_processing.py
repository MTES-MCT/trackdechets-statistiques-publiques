"""
Data gathering and processing
"""
from datetime import datetime
from typing import Tuple

import polars as pl
import geopandas as gpd
from shapely.geometry import Point

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
        if date_interval is not None:
            bs_created_total += (
                df.filter(pl.col("semaine").is_between(*date_interval, closed="left")).select(stat_column).sum().item()
            )
        else:
            bs_created_total += df.select(stat_column).sum().item()

    return bs_created_total


def get_total_quantity_processed(
    all_bordereaux_data: dict[str, pl.DataFrame],
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
    for _, df in all_bordereaux_data.items():
        if date_interval is not None:
            quantity_processed_total += (
                df.filter(pl.col("semaine").is_between(*date_interval, closed="left"))
                .select("quantite_traitee_operations_finales")
                .sum()
                .fill_null(0)
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


def create_installations_geojson(
    df_installations: pl.DataFrame,
    df_installations_waste_processed: pl.DataFrame,
    rubrique: str,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> str:
    df_installations_filtered = df_installations.filter(pl.col("rubrique") == rubrique)

    df_installations_filtered = df_installations_filtered.group_by("code_aiot").agg(
        pl.col("siret"),
        pl.col("quantite_autorisee").sum(),
        pl.col("latitude").max(),
        pl.col("longitude").max(),
        pl.col("raison_sociale").max(),
        pl.col("etat_activite").max(),
        pl.col("regime").max(),
        pl.col("unite").max(),
        pl.col("adresse1").max(),
        pl.col("adresse2").max(),
        pl.col("code_postal").max(),
        pl.col("commune").max(),
    )

    df_waste_processed_filtered = df_installations_waste_processed.filter(
        (pl.col("rubrique") == rubrique) & (pl.col("day_of_processing").is_between(*date_interval, closed="left"))
    )

    agg_expr = pl.col("quantite_traitee").sum().alias("cumul_quantite_traitee")
    if rubrique in ["2790", "2770"]:
        agg_expr = pl.col("quantite_traitee").mean().alias("moyenne_quantite_journaliere_traitee")
    df_stats = df_waste_processed_filtered.group_by("code_aiot").agg(agg_expr)

    df_graphs = (
        df_waste_processed_filtered.filter(pl.col("day_of_processing").is_not_null())
        .group_by("code_aiot")
        .map_groups(lambda x: create_icpe_graph(x, "code_aiot", rubrique))
    )

    df_installations_final = df_installations_filtered.join(df_stats, on="code_aiot", how="left", validate="1:1").join(
        df_graphs, on="code_aiot", how="left", validate="1:1"
    )

    df_installations_final = df_installations_final.to_pandas()
    df_installations_final["siret"] = df_installations_final["siret"].str.join(", ")

    gdf_installations = gpd.GeoDataFrame(df_installations_final)
    gdf_installations = gdf_installations.set_geometry(
        gdf_installations.apply(lambda x: Point(x["longitude"], x["latitude"]), axis=1)
    )

    return gdf_installations.to_json()


def create_regional_geojson(
    df_regional_waste_processed: pl.DataFrame,
    regional_geodataframe: gpd.GeoDataFrame,
    rubrique: str,
    regional_key_column: str,
    date_interval: Tuple[datetime, datetime] | None = None,
) -> str:
    gdf = regional_geodataframe

    df_waste_processed_filtered = df_regional_waste_processed.filter(
        (pl.col("rubrique") == rubrique)
        & (
            pl.col("day_of_processing").is_between(*date_interval, closed="left")
            | pl.col("day_of_processing").is_null()
        )
    ).with_columns(pl.col(regional_key_column).cast(pl.String))

    # Add annual stats and authorized quantity by departement/region
    agg_expr = pl.col("quantite_traitee").mean().alias("moyenne_quantite_journaliere_traitee").fill_null(0)
    if rubrique == "2760-1":
        agg_expr = pl.col("quantite_traitee").sum().alias("cumul_quantite_traitee").fill_null(0)

    annual_stats = df_waste_processed_filtered.group_by(regional_key_column).agg(
        [agg_expr, pl.col("quantite_autorisee").max(), pl.col("nombre_installations").max()]
    )
    gdf = gdf.merge(
        annual_stats.to_pandas(),
        left_on="code",
        right_on=regional_key_column,
        how="left",
        validate="1:1",
    )

    # Create plotly graphs adding to daily waste processed the authorized quantity for each departement/region
    df_graphs = (
        df_waste_processed_filtered.filter(pl.col("day_of_processing").is_not_null())
        .group_by(regional_key_column)
        .map_groups(lambda x: create_icpe_graph(x, key_column=regional_key_column, rubrique=rubrique))
    )

    gdf = gdf.merge(
        df_graphs.to_pandas(),
        left_on="code",
        right_on=regional_key_column,
        how="left",
        validate="one_to_one",
    )

    return gdf.to_json()
