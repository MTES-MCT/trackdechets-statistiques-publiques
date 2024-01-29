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

waste_processed_by_naf_annual_stats_sql = """
select
    *
from
    refined_zone_stats_publiques.annual_waste_produced_by_naf
"""

installations_icpe_sql = """
select 
    * 
from 
    refined_zone_stats_publiques.installations_icpe
"""

waste_processed_icpe_sql = """
select
    siret,
    rubrique,
    raison_sociale,
    quantite_autorisee,
    day_of_processing,
    quantite_traitee
from
    refined_zone_icpe.installations_daily_processed_wastes
"""
