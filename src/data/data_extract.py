import json
import logging
import os
import tempfile
import time

import polars as pl
import sshtunnel
from django.conf import settings
from sqlalchemy import create_engine

from data.utils import format_waste_codes

DB_ENGINE = create_engine(settings.WAREHOUSE_URL)
SQL_PATH = settings.BASE_DIR / "data" / "sql"
STATIC_DATA_PATH = settings.BASE_DIR / "data" / "static"

logger = logging.getLogger(__name__)

FLOAT_COLUMNS = [
    "quantite_tracee",
    "quantite_emise",
    "quantite_envoyee",
    "quantite_recue",
    "quantite_traitee",
    "quantite_traitee_operations_non_finales",
    "quantite_traitee_operations_finales",
    "quantite_produite",
]


def extract_dataset(sql_string: str) -> pl.DataFrame:
    started_time = time.time()

    # Create SSH KEY:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as fp:
        fp.write(settings.DWH_SSH_KEY)
        fp.close()

        os.chmod(fp.name, 0o600)

        with sshtunnel.open_tunnel(
            (settings.DWH_SSH_HOST, int(settings.DWH_SSH_PORT)),
            ssh_username=settings.DWH_SSH_USERNAME,
            ssh_pkey=fp.name,
            remote_bind_address=("localhost", int(settings.DWH_PORT)),
        ) as tunnel:
            local_port = tunnel.local_bind_port
            local_host = tunnel.local_bind_host

            SQLALCHEMY_DATABASE_URL = (
                f"clickhouse+native://{settings.DWH_USERNAME}:{settings.DWH_PASSWORD}@{local_host}:{local_port}"
            )

            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            data_df = pl.read_database(sql_string, connection=engine)
            for colname, data_type in data_df.schema.items():
                if (data_type == pl.String) and (colname in FLOAT_COLUMNS):
                    data_df = data_df.with_columns(pl.col(colname).cast(pl.Float64))

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
        "SELECT * FROM trusted_zone.codes_operations_traitements", uri=settings.WAREHOUSE_URL, engine="adbc"
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
        "SELECT * FROM trusted_zone_insee.code_geo_departements", uri=settings.WAREHOUSE_URL, engine="adbc"
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
    data = pl.read_database_uri("SELECT * FROM trusted_zone.code_dechets", uri=settings.WAREHOUSE_URL, engine="adbc")
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
