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

icpe_installations_sql = """
select 
    * 
from 
    refined_zone_stats_publiques.installations_icpe_2024
"""

icpe_installations_waste_processed_sql = """
select
    *
from
    refined_zone_stats_publiques.icpe_installations_daily_processed_waste
"""

icpe_departements_waste_processed_sql = """
select
    *
from
    refined_zone_stats_publiques.icpe_departements_daily_processed_waste
"""

icpe_regions_waste_processed_sql = """
select
    *
from
    refined_zone_stats_publiques.icpe_regions_daily_processed_waste
"""

icpe_france_waste_processed_sql = """
select
    *
from
    refined_zone_stats_publiques.icpe_france_daily_processed_waste
"""
