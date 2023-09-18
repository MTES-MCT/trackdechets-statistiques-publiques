import pytest

from ..factories import ComputationFactory

pytestmark = pytest.mark.django_db


def test_home_no_content():
    computation = ComputationFactory()

    assert computation.pk
