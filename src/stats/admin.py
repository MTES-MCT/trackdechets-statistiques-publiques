from django.contrib import admin

from .models import Computation


@admin.register(Computation)
class ComputationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "year",
        "created",
    ]
