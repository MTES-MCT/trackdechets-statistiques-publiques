import datetime as dt

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import Http404
from django.views.generic import TemplateView

from stats.models import Computation


class BaseRender(TemplateView):
    def handle_missing_computation(self, year):
        pass

    def get_current_year(self):
        """Today's year"""
        return dt.date.today().year

    def get_year(self):
        """View's year"""
        return self.get_current_year()

    def get_context_data(self, **kwargs):
        year = self.get_year()
        ctx = super().get_context_data(**kwargs)
        computation = Computation.objects.filter(year=year).first()
        if not computation:
            self.handle_missing_computation(year)
        ctx["computation"] = computation
        ctx["current_year"] = self.get_current_year()
        return ctx


class Main(BaseRender):
    template_name = "stats/stats.html"


class CurrentStats(BaseRender):
    def handle_missing_computation(self, year):
        body = f"Trackdéchets Statistiques publiques - aucune donnée pour {year}"
        message = EmailMessage(
            subject="Trackdéchets Statistiques publiques - Anomalie",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=settings.MESSAGE_RECIPIENTS,
        )
        message.send()

    template_name = "stats/yearly.html"


class LastStats(CurrentStats):
    def get_year(self):
        return dt.date.today().year - 1


class BaseBsdView(BaseRender):
    def get_year(self):
        current_year = dt.date.today().year
        year = self.kwargs.get("year")
        allowed = [current_year, current_year - 1]
        if year not in allowed:
            raise Http404
        return year


class BsddView(BaseBsdView):
    template_name = "stats/fragments/bsdd.html"


class BsdaView(BaseBsdView):
    template_name = "stats/fragments/bsda.html"


class BsdasriView(BaseBsdView):
    template_name = "stats/fragments/bsdasri.html"


class BsffView(BaseBsdView):
    template_name = "stats/fragments/bsff.html"


class CompanyView(BaseBsdView):
    template_name = "stats/fragments/company.html"


class UserView(BaseBsdView):
    template_name = "stats/fragments/user.html"
