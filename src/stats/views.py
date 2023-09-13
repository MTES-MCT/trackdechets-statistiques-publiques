import datetime as dt

from django.conf import settings
from django.core.mail import EmailMessage
from django.views.generic import TemplateView

from stats.models import Computation


class BaseRender(TemplateView):
    def handle_missing_computation(self, year):
        pass

    def get_current_year(self):
        return dt.date.today().year

    def get_year(self):
        return self.get_current_year()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        computation = Computation.objects.filter(year=self.get_year()).first()
        if not computation:
            self.handle_missing_computation(self.get_year())
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


class BsddView(BaseRender):
    template_name = "stats/fragments/bsdd.html"


class BsdaView(BaseRender):
    template_name = "stats/fragments/bsda.html"


class BsdasriView(BaseRender):
    template_name = "stats/fragments/bsdasri.html"


class BsffView(BaseRender):
    template_name = "stats/fragments/bsff.html"


class CompanyView(BaseRender):
    template_name = "stats/fragments/company.html"


class UserView(BaseRender):
    template_name = "stats/fragments/user.html"
