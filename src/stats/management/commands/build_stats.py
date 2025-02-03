from django.core.management.base import BaseCommand

from ...processors.clear import clear_figs
from ...processors.create_df import build_dataframes
from ...processors.stats_processor import build_stats_and_figs


class Command(BaseCommand):
    def handle(self, verbosity=0, **options):
        build_dataframes()

        clear_figs()

        for year in [2022, 2023, 2024, 2025]:
            build_stats_and_figs(year, clear_year=True)
