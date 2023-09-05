import datetime as dt

from django.core.management.base import BaseCommand

from ...processors.create_figs import build_figs


class Command(BaseCommand):
    def handle(self, verbosity=0, **options):
        year = dt.date.today().year
        build_figs(year - 1)
        build_figs(year, clear_year=True)
