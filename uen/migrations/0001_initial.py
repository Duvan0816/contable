# Generated by Django 5.0.8 on 2025-01-07 19:35

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuario', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auxiliar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.PositiveIntegerField()),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Rubro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.PositiveIntegerField()),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Rubro',
                'verbose_name_plural': 'Rubros',
            },
        ),
        migrations.CreateModel(
            name='CentroCostos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.PositiveIntegerField()),
                ('nombre', models.CharField(max_length=100)),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centrocostos', to='usuario.area')),
                ('regional', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centrocostos', to='usuario.regional')),
                ('uen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centrocostos', to='usuario.uen')),
            ],
        ),
        migrations.CreateModel(
            name='Presupuesto',
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
                ('cuenta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presupuestos', to='uen.centrocostos')),
                ('uen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presupuestos', to='usuario.uen')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='presupuesto', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PresupuestoActualizado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rubro', models.IntegerField()),
                ('subrubro', models.IntegerField()),
                ('auxiliar', models.IntegerField(default=0)),
                ('item', models.IntegerField()),
                ('updatedRubros', models.JSONField(blank=True, null=True)),
                ('monthlyTotals', models.JSONField(blank=True, null=True)),
                ('rubrosTotals', models.JSONField(blank=True, null=True)),
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
                ('presupuestomes', models.DecimalField(decimal_places=0, default=0.0, max_digits=20)),
                ('presupuesto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meses_presupuesto', to='uen.presupuestoactualizado')),
            ],
        ),
        migrations.CreateModel(
            name='PresupuestoProyectado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meses', models.IntegerField()),
                ('presupuestomes', models.DecimalField(decimal_places=0, default=0.0, max_digits=20)),
                ('presupuesto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meses_presupuesto', to='uen.presupuesto')),
            ],
        ),
        migrations.CreateModel(
            name='SubRubro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.PositiveIntegerField()),
                ('nombre', models.CharField(max_length=100)),
                ('rubro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subrubros', to='uen.rubro')),
            ],
        ),
        migrations.CreateModel(
            name='PresupuestoTotal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('proyectado', models.BigIntegerField(default=0)),
                ('ejecutado', models.BigIntegerField(blank=True, default=0, null=True)),
                ('auxiliar', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PresupuestoTotales', to='uen.auxiliar')),
                ('cuenta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='PresupuestoTotales', to='uen.centrocostos')),
                ('rubro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PresupuestoTotal', to='uen.rubro')),
                ('subrubro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PresupuestoTotales', to='uen.subrubro')),
            ],
        ),
        migrations.AddField(
            model_name='auxiliar',
            name='subrubro',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='auxiliares', to='uen.subrubro'),
        ),
        migrations.AddIndex(
            model_name='centrocostos',
            index=models.Index(fields=['regional'], name='uen_centroc_regiona_a51504_idx'),
        ),
        migrations.AddIndex(
            model_name='presupuesto',
            index=models.Index(fields=['uen', 'cuenta', 'fecha'], name='uen_presupu_uen_id_2c791b_idx'),
        ),
    ]
