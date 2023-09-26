import os
import shutil

from data.data_extract import get_company_data, get_user_data
from data.datasets import get_data_df


def build_dataframes():
    # store dataframes as json in temp files
    root = r"temp_data"  # unversionned dir
    try:
        shutil.rmtree(root)
    except FileNotFoundError:
        pass
    os.mkdir(root)

    bsd_data = get_data_df()

    bsd_data.bsdd_data.write_json("temp_data/bsdd_data.json")
    bsd_data.bsda_data.write_json("temp_data/bsda_data.json")
    bsd_data.bsdasri_data.write_json("temp_data/bsdasri_data.json")
    bsd_data.bsff_data.write_json("temp_data/bsff_data.json")
    bsd_data.all_bsds_data.write_json("temp_data/all_bsds_data.json")
    get_company_data().write_json("temp_data/company_data.json")
    get_user_data().write_json("temp_data/user_data.json")

    for dataset_name in [
        "bsdd_weekly_data",
        "bsda_weekly_data",
        "bsff_weekly_data",
        "bsdasri_weekly_data",
        "accounts_weekly_data",
        "annual_waste_processed_data",
        "accounts_by_naf_data",
        "waste_processed_by_naf_annual_stats",
    ]:
        getattr(bsd_data, dataset_name).write_parquet(f"temp_data/{dataset_name}.parquet")
