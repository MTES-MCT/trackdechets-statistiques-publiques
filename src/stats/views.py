import datetime as dt

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import Http404, JsonResponse
from django.views.generic import TemplateView

from stats.models import Computation


class BaseRender(TemplateView):
    template_name = "stats/yearly.html"

    def get_current_year(self):
        """Today's year"""
        return dt.date.today().year

    def get_year(self):
        """View's year"""

        year = self.kwargs.get("year")
        if year is None:
            last_computation = Computation.objects.order_by("year").last()
            if not last_computation:
                return None
            return last_computation.year
        return year

    def handle_missing_computation(self, year):
        body = f"Trackdéchets Statistiques publiques - aucune donnée pour {year}"
        message = EmailMessage(
            subject="Trackdéchets Statistiques publiques - Anomalie",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=settings.MESSAGE_RECIPIENTS,
        )
        message.send()

    def get_context_data(self, **kwargs):
        year = self.get_year()

        ctx = super().get_context_data(**kwargs)
        computation = None
        if year:
            computation = Computation.objects.filter(year=year).first()
        if not computation:
            self.handle_missing_computation(year)
        ctx["computation"] = computation
        return ctx


class Main(BaseRender):
    template_name = "stats/stats.html"


class BaseBsdView(BaseRender):
    def get_year(self):
        year = self.kwargs.get("year")
        allowed = [2022, 2023, 2024]
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


class BsvhuView(BaseBsdView):
    template_name = "stats/fragments/bsvhu.html"


class CompanyView(BaseBsdView):
    template_name = "stats/fragments/company.html"


class UserView(BaseBsdView):
    template_name = "stats/fragments/user.html"


def digest_view(request):
    """Minimal api to retrieve main numbers for td home page."""
    last_computation = Computation.objects.order_by("year").last()
    digest = {}
    if last_computation:
        digest = {
            "total_bsdd_created": last_computation.total_bs_created,
            "total_quantity_processed": last_computation.total_quantity_processed,
            "total_companies": last_computation.total_companies_created,
        }
    return JsonResponse(digest)
