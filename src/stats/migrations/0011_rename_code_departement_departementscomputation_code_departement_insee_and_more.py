# Generated by Django 5.0.1 on 2024-02-07 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0010_alter_installationscomputation_siret"),
    ]

    operations = [
        migrations.RenameField(
            model_name="departementscomputation",
            old_name="code_departement",
            new_name="code_departement_insee",
        ),
        migrations.RenameField(
            model_name="departementscomputation",
            old_name="code_region",
            new_name="code_region_insee",
        ),
        migrations.RenameField(
            model_name="regionscomputation",
            old_name="code_region",
            new_name="code_region_insee",
        ),
        migrations.RemoveField(
            model_name="departementscomputation",
            name="stats",
        ),
        migrations.RemoveField(
            model_name="regionscomputation",
            name="stats",
        ),
        migrations.AddField(
            model_name="departementscomputation",
            name="cumul_quantite_traitee",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="departementscomputation",
            name="moyenne_quantite_journaliere_traitee",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="departementscomputation",
            name="nombre_installations",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="departementscomputation",
            name="quantite_autorisee",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="departementscomputation",
            name="taux_consommation",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="installationscomputation",
            name="taux_consommation",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="regionscomputation",
            name="cumul_quantite_traitee",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="regionscomputation",
            name="moyenne_quantite_journaliere_traitee",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="regionscomputation",
            name="nombre_installations",
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name="regionscomputation",
            name="quantite_autorisee",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="regionscomputation",
            name="taux_consommation",
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name="departementscomputation",
            name="graph",
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AlterField(
            model_name="regionscomputation",
            name="graph",
            field=models.JSONField(default=dict, null=True),
        ),
    ]