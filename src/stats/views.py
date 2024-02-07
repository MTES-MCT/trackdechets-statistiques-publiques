import datetime as dt
import json
import math

from django.conf import settings
from django.core.mail import EmailMessage
from django.http import Http404, JsonResponse
from django.views.generic import TemplateView

from stats.models import Computation, DepartementsComputation, InstallationsComputation, RegionsComputation


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
        allowed = [2022, 2023]
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


def icpe_view_many(request, layer, year, rubrique):
    metric_name = "moyenne_quantite_journaliere_traitee"
    if rubrique == "2760-1":
        metric_name = "cumul_quantite_traitee"

    layers_configs = {
        "installations": {
            "cls": InstallationsComputation,
            "fields": [
                "code_aiot",
                "latitude",
                "longitude",
                "raison_sociale",
                "siret",
                "adresse1",
                "adresse2",
                "code_postal",
                "commune",
                "etat_activite",
                "regime",
                "unite",
                "quantite_autorisee",
                "taux_consommation",
                metric_name,
            ],
            "layer_key": "code_aiot",
        },
        "regions": {
            "cls": RegionsComputation,
            "fields": [
                "code_region_insee",
                "nom_region",
                "quantite_autorisee",
                "taux_consommation",
                metric_name,
                "nombre_installations",
            ],
            "layer_key": "code_region_insee",
        },
        "departements": {
            "cls": DepartementsComputation,
            "fields": [
                "code_departement_insee",
                "nom_departement",
                "quantite_autorisee",
                "taux_consommation",
                metric_name,
                "nombre_installations",
            ],
            "layer_key": "code_departement_insee",
        },
    }

    layer_config = layers_configs[layer]
    model = layer_config["cls"]
    fields = layer_config["fields"]
    layer_key = layer_config["layer_key"]

    results = {}
    for obj in model.objects.filter(year=year, rubrique=rubrique).values(*fields):
        obj_clean = {
            k: e if not isinstance(e, float) or not (math.isnan(e) or math.isinf(e)) else None for k, e in obj.items()
        }
        results[obj_clean[layer_key]] = obj_clean

    if not results:
        raise Http404

    return JsonResponse({"data": results})


def icpe_get_graph(request, layer, year, rubrique, code):
    layers_configs = {
        "installations": {
            "cls": InstallationsComputation,
            "specific_filter": {"code_aiot": code},
        },
        "regions": {
            "cls": RegionsComputation,
            "specific_filter": {"code_region_insee": code},
        },
        "departements": {
            "cls": DepartementsComputation,
            "specific_filter": {"code_departement_insee": code},
        },
    }

    layer_config = layers_configs[layer]
    model = layer_config["cls"]
    specific_filter = layer_config["specific_filter"]
    result = model.objects.filter(year=year, rubrique=rubrique, **specific_filter).values("graph").first()

    if not result:
        raise Http404

    return JsonResponse({"graph": json.loads(result["graph"])})
