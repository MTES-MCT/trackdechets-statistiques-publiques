import pytest
from django.urls import reverse

from ..factories import ComputationFactory

pytestmark = pytest.mark.django_db


def test_home_no_content(anon_client):
    url = reverse("main")
    res = anon_client.get(url)
    assert res.status_code == 200
    assert "Nous avons rencontré un problème" in res.content.decode()


def test_home_with_content(anon_client):
    ComputationFactory()
    url = reverse("main")
    res = anon_client.get(url)
    assert res.status_code == 200
    assert "Cette page publique présente les données disponibles sur Trackdéchets." in res.content.decode()
