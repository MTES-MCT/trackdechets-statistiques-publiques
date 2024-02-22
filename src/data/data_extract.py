import json
import logging
import time

import polars as pl
from django.conf import settings
from sqlalchemy import create_engine

from data.utils import format_waste_codes

DB_ENGINE = create_engine(settings.WAREHOUSE_URL)
SQL_PATH = settings.BASE_DIR / "data" / "sql"
STATIC_DATA_PATH = settings.BASE_DIR / "data" / "static"

logger = logging.getLogger(__name__)


def extract_dataset(sql_string: str) -> pl.DataFrame:
    started_time = time.time()

    data_df = pl.read_database_uri(sql_string, uri=settings.WAREHOUSE_URL)
    for col in ["semaine", "day_of_processing"]:
        if col in data_df.columns:
            data_df = data_df.with_columns(pl.col(col).dt.replace_time_zone(None))
    logger.info(
        "Loading stats duration: %s (query : %s)",
        time.time() - started_time,
        sql_string,
    )

    return data_df


def get_processing_operation_codes_data() -> pl.DataFrame:
    """
    Returns description for each processing operation codes.

    Returns
    --------
    DataFrame
        DataFrame with processing operations codes and description.
    """
    data = pl.read_database_uri(
        "SELECT * FROM trusted_zone.codes_operations_traitements",
        uri=settings.WAREHOUSE_URL,
    )

    return data


def get_departement_geographical_data() -> pl.DataFrame:
    """
    Returns INSEE department geographical data.

    Returns
    --------
    DataFrame
        DataFrame with INSEE department geographical data.
    """
    data = pl.read_database_uri(
        "SELECT * FROM trusted_zone_insee.code_geo_departements",
        uri=settings.WAREHOUSE_URL,
    )

    return data


def get_waste_nomenclature_data() -> pl.DataFrame:
    """
    Returns waste nomenclature data.

    Returns
    --------
    DataFrame
        DataFrame with waste nomenclature data.
    """
    data = pl.read_database_uri("SELECT * FROM trusted_zone.code_dechets", uri=settings.WAREHOUSE_URL)
    return data


def get_waste_code_hierarchical_nomenclature() -> list[dict]:
    """
    Returns waste code nomenclature in a hierarchical way, to use with tree components.

    Returns
    --------
    list of dicts
        Each dict contains the data necessary for the TreeComponent along with childrens.
    """
    with (STATIC_DATA_PATH / "waste_codes.json").open() as f:
        waste_code_hierarchy = json.load(f)

    return format_waste_codes(waste_code_hierarchy, add_top_level=True)
