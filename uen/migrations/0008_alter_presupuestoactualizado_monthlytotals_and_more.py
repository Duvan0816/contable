# Generated by Django 5.0.8 on 2024-11-04 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uen', '0007_presupuestoactualizado_presupuestomes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presupuestoactualizado',
            name='monthlyTotals',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='presupuestoactualizado',
            name='rubrosTotals',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='presupuestoactualizado',
            name='updatedRubros',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
