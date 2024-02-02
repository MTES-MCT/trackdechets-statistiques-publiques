from django.core.management.base import BaseCommand

from ...processors.clear import clear_figs
from ...processors.create_df import build_dataframes
from ...processors.create_figs import build_figs


class Command(BaseCommand):
    def handle(self, verbosity=0, **options):
        build_dataframes()

        clear_figs()

        build_figs(2022, clear_year=True)

        build_figs(2023, clear_year=True)

        build_figs(2024, clear_year=True)
