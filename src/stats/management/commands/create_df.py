from django.core.management.base import BaseCommand

from ...processors.create_df import build_dataframes


class Command(BaseCommand):
    def handle(self, verbosity=0, **options):
        build_dataframes()
