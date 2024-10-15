# Generated by Django 5.0.8 on 2024-10-13 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uen', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PresupuestoTotal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('total_presupuesto', models.DecimalField(decimal_places=0, max_digits=10)),
                ('fecha', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='presupuesto',
            name='presupuestomes',
            field=models.DecimalField(decimal_places=0, default=0.0, max_digits=10),
        ),
    ]