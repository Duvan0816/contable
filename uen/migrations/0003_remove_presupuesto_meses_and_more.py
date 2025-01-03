# Generated by Django 5.0.8 on 2024-10-29 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uen', '0002_alter_presupuesto_presupuestomes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='presupuesto',
            name='meses',
        ),
        migrations.RemoveField(
            model_name='presupuesto',
            name='presupuestomes',
        ),
        migrations.CreateModel(
            name='PresupuestoMes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes', models.IntegerField()),
                ('monto', models.DecimalField(decimal_places=0, default=0.0, max_digits=15)),
                ('presupuesto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meses_presupuesto', to='uen.presupuesto')),
            ],
        ),
    ]
