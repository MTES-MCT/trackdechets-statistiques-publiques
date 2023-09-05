from django.urls import path

from .views import BsdasriView, BsdaView, BsddView, BsffView, CompanyView, CurrentStats, LastStats, UserView

urlpatterns = [
    path("stats-current", CurrentStats.as_view(), name="current_stats"),
    path("stats-last", LastStats.as_view(), name="last_stats"),
    path("bsdd", BsddView.as_view(), name="bsdd"),
    path("bsda", BsdaView.as_view(), name="bsda"),
    path("bsdasri", BsdasriView.as_view(), name="bsdasri"),
    path("bsff", BsffView.as_view(), name="bsff"),
    path("companies", CompanyView.as_view(), name="companies"),
    path("users", UserView.as_view(), name="users"),
]
