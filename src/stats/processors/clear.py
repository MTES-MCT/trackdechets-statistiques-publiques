import datetime as dt

from ..models import Computation


def clear_figs():
    # clear data than year - 1
    Computation.objects.filter(year__lt=dt.date.today().year - 1)
