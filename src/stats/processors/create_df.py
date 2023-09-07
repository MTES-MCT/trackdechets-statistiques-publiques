import os
import shutil

from data.data_extract import get_company_data, get_user_data
from data.datasets import get_data_pd


def build_dataframes():
    root = r"temp_data"
    try:
        shutil.rmtree(root)
    except FileNotFoundError:
        pass
    os.mkdir(root)

    bsd_data = get_data_pd()

    bsd_data.bsdd_data.write_json("temp_data/bsdd_data.json")
    bsd_data.bsda_data.write_json("temp_data/bsda_data.json")
    bsd_data.bsdasri_data.write_json("temp_data/bsdasri_data.json")
    bsd_data.bsff_data.write_json("temp_data/bsff_data.json")
    bsd_data.all_bsds_data.write_json("temp_data/all_bsds_data.json")
    get_company_data().write_json("temp_data/company_data.json")
    get_user_data().write_json("temp_data/user_data.json")
