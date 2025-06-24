import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Computation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    year = models.PositiveSmallIntegerField(default=2023)
    created = models.DateTimeField(_("Created"), default=timezone.now)

    total_bs_created = models.PositiveBigIntegerField(default=0)
    total_quantity_processed = models.PositiveBigIntegerField(default=0)
    total_quantity_processed_non_dangerous = models.PositiveBigIntegerField(default=0)
    total_companies_created = models.PositiveBigIntegerField(default=0)

    quantity_processed_total = models.JSONField(default=dict)

    quantity_processed_yearly = models.JSONField(default=dict)
    quantity_processed_non_dangerous_yearly = models.PositiveBigIntegerField(default=0)
    bs_created_yearly = models.JSONField(default=dict)

    quantity_processed_weekly = models.JSONField(default=dict)
    quantity_processed_sunburst = models.JSONField(default=dict)
    bsdd_counts_weekly = models.JSONField(default=dict)
    bsda_counts_weekly = models.JSONField(default=dict)
    bsff_counts_weekly = models.JSONField(default=dict)
    bsff_packagings_counts_weekly = models.JSONField(default=dict)
    bsdasri_counts_weekly = models.JSONField(default=dict)
    bsvhu_counts_weekly = models.JSONField(default=dict)
    bsd_non_dangerous_counts_weekly = models.JSONField(default=dict)

    bsdd_quantities_weekly = models.JSONField(default=dict)
    bsda_quantities_weekly = models.JSONField(default=dict)
    bsff_quantities_weekly = models.JSONField(default=dict)
    bsdasri_quantities_weekly = models.JSONField(default=dict)
    bsvhu_quantities_weekly = models.JSONField(default=dict)
    bsd_non_dangerous_quantities_weekly = models.JSONField(default=dict)

    bsdd_bordereaux_created = models.PositiveBigIntegerField(default=0)
    bsda_bordereaux_created = models.PositiveBigIntegerField(default=0)
    bsff_bordereaux_created = models.PositiveBigIntegerField(default=0)
    bsdasri_bordereaux_created = models.PositiveBigIntegerField(default=0)
    bsvhu_bordereaux_created = models.PositiveBigIntegerField(default=0)
    bsd_non_dangerous_bordereaux_created = models.PositiveBigIntegerField(default=0)

    bsdd_quantity_processed = models.PositiveBigIntegerField(default=0)
    bsda_quantity_processed = models.PositiveBigIntegerField(default=0)
    bsff_quantity_processed = models.PositiveBigIntegerField(default=0)
    bsdasri_quantity_processed = models.PositiveBigIntegerField(default=0)
    bsvhu_quantity_processed = models.PositiveBigIntegerField(default=0)
    bsd_non_dangerous_quantity_processed = models.PositiveBigIntegerField(default=0)

    mean_quantity_by_bsff_packagings = models.FloatField(default=0, null=True)
    mean_packagings_by_bsff = models.FloatField(default=0, null=True)

    produced_quantity_by_category = models.JSONField(default=dict)

    company_created_total_life = models.JSONField(default=dict)
    user_created_total_life = models.JSONField(default=dict)

    company_created_weekly = models.JSONField(default=dict)
    user_created_weekly = models.JSONField(default=dict)

    company_counts_by_category = models.JSONField(default=dict)
    icpe_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = _("Computation")
        verbose_name_plural = _("Computations")
        ordering = ("-created",)
        app_label = "stats"
