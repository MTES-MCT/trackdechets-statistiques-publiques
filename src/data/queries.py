bs_weekly_data_sql = """
select
    *
from
    {}
where
    semaine >= '2020-01-01'
"""

accounts_weekly_stats_sql = """
select
    *
from
    refined_zone_stats_publiques.accounts_created_by_week
where
    semaine >= '2020-01-01'
"""

weekly_waste_processed_stats_sql = """
select
    *
from
    refined_zone_stats_publiques.weekly_waste_processed_stats
where
    semaine >= '2020-01-01'
"""


accounts_by_naf_annual_stats_sql = """
select
    *
from
    refined_zone_stats_publiques.annual_company_accounts_created_by_naf
"""

waste_produced_by_naf_annual_stats_sql = """
select
    *
from
    refined_zone_stats_publiques.annual_waste_produced_by_naf
"""
