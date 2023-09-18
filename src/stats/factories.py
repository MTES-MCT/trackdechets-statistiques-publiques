import factory

from .models import Computation


class ComputationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Computation

    year = 2023
