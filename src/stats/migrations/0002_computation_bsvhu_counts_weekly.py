# Generated by Django 4.2.5 on 2023-11-06 10:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stats", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="computation",
            name="bsvhu_counts_weekly",
            field=models.JSONField(default=dict),
        ),
    ]
