from django.urls import path

from .views import BaseRender, BsdasriView, BsdaView, BsddView, BsffView, BsvhuView, CompanyView, UserView, digest_view

urlpatterns = [
    path("stats/", BaseRender.as_view(), name="last_stats"),
    path("stats/<int:year>", BaseRender.as_view(), name="yearly_stats"),
    path("bsdd/<int:year>", BsddView.as_view(), name="bsdd"),
    path("bsda/<int:year>", BsdaView.as_view(), name="bsda"),
    path("bsdasri/<int:year>", BsdasriView.as_view(), name="bsdasri"),
    path("bsff/<int:year>", BsffView.as_view(), name="bsff"),
    path("bsvhu/<int:year>", BsvhuView.as_view(), name="bsvhu"),
    path("companies/<int:year>", CompanyView.as_view(), name="companies"),
    path("users/<int:year>", UserView.as_view(), name="users"),
    path("digest/", digest_view, name="stats_digest"),
]
