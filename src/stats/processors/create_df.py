import os
import shutil

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

    for dataset_name in [
        "bsdd_weekly_data",
        "bsda_weekly_data",
        "bsff_weekly_data",
        "bsdasri_weekly_data",
        "bsvhu_weekly_data",
        "accounts_weekly_data",
        "weekly_waste_processed_data",
        "accounts_by_naf_data",
        "waste_processed_by_naf_annual_stats",
    ]:
        getattr(bsd_data, dataset_name).write_parquet(f"temp_data/{dataset_name}.parquet")
