# Generated by Django 5.0.8 on 2024-11-04 20:15

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uen', '0006_presupuesto_meses_presupuesto_presupuestomes_and_more'),
        ('usuario', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PresupuestoActualizado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rubro', models.IntegerField()),
                ('subrubro', models.IntegerField()),
                ('auxiliar', models.IntegerField(default=0)),
                ('item', models.IntegerField()),
                ('updatedRubros', models.JSONField(null=True)),
                ('monthlyTotals', models.JSONField(null=True)),
                ('rubrosTotals', models.JSONField(null=True)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('cuenta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presupuestos_actualizado', to='uen.centrocostos')),
                ('uen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presupuestos_actualizado', to='usuario.uen')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='presupuesto_actualizado', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PresupuestoMes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meses', models.IntegerField()),
                ('presupuestomes', models.DecimalField(decimal_places=0, default=0.0, max_digits=15)),
                ('presupuesto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meses_presupuesto', to='uen.presupuestoactualizado')),
            ],
        ),
    ]
