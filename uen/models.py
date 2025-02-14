# UEN models.py
from django.db import models
from usuario.models import UEN, Regional, CustomUser, Area
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
# Create your models here.    
class CentroCostos(models.Model):
    codigo = models.PositiveIntegerField()
    nombre = models.CharField(max_length=100)
    regional = models.ForeignKey(Regional, related_name="centrocostos", on_delete=models.CASCADE, null=True, blank=True)
    uen = models.ForeignKey(UEN, related_name="centrocostos", on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, related_name="centrocostos", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['regional']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.regional} - {self.uen}"
    
class Rubro (models.Model):
    codigo = models.PositiveIntegerField()
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Rubro"
        verbose_name_plural = "Rubros"

    def __str__(self):
        return self.nombre
    
class SubRubro (models.Model):
    codigo = models.PositiveIntegerField()
    nombre = models.CharField(max_length=100)
    rubro = models.ForeignKey(Rubro, related_name="subrubros", on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return  f"{self.codigo} {self.nombre}"

class Auxiliar (models.Model):
    codigo = models.PositiveIntegerField()
    nombre = models.CharField(max_length=100)
    subrubro = models.ForeignKey(SubRubro, related_name="auxiliares", on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.nombre


class PresupuestoActualizado(models.Model):
    usuario = models.ForeignKey(CustomUser, related_name="presupuesto_actualizado", on_delete=models.CASCADE, null=True, blank=True)
    cuenta = models.ForeignKey(CentroCostos, related_name="presupuestos_actualizado", on_delete=models.SET_NULL, null=True, blank=True)
    uen = models.ForeignKey(UEN, related_name="presupuestos_actualizado", on_delete=models.SET_NULL, null=True, blank=True)
    rubro = models.IntegerField()
    subrubro = models.IntegerField()
    auxiliar = models.IntegerField(default=0)
    item = models.IntegerField()
    updatedRubros = models.JSONField(null=True, blank=True)
    monthlyTotals = models.JSONField(null=True, blank=True)
    rubrosTotals = models.JSONField(null=True, blank=True)
    fecha = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.usuario and self.usuario.email == '':
            self.fecha = timezone.now().date()
        else:
            self.fecha = timezone.now().replace(year=timezone.now().year)

        super(PresupuestoActualizado, self).save(*args, **kwargs)

    def __str__(self):
        return f"Presupuesto {self.cuenta} - Fecha {self.fecha}"


class PresupuestoMes(models.Model):
    presupuesto = models.ForeignKey(PresupuestoActualizado, related_name="meses_presupuesto", on_delete=models.CASCADE)
    meses = models.IntegerField()
    presupuestomes = models.DecimalField(max_digits=20, decimal_places=0, default=0.00)

    def __str__(self):
        return f"Presupuesto {self.presupuesto.id} - Mes {self.meses} - Monto {self.presupuestomes}"


class Presupuesto(models.Model):
    usuario = models.ForeignKey(CustomUser, related_name="presupuesto", on_delete=models.CASCADE, null=True, blank=True)
    cuenta = models.ForeignKey(CentroCostos, related_name="presupuestos", on_delete=models.SET_NULL, null=True, blank=True)
    uen = models.ForeignKey(UEN, related_name="presupuestos", on_delete=models.SET_NULL, null=True, blank=True)
    rubro = models.IntegerField()
    subrubro = models.IntegerField()
    auxiliar = models.IntegerField(default=0)
    item = models.IntegerField()
    updatedRubros = models.JSONField(null=True)
    monthlyTotals = models.JSONField(null=True)
    rubrosTotals = models.JSONField(null=True)
    fecha = models.DateField(default=timezone.now)

    class Meta:
        indexes = [    
            models.Index(fields=['uen', 'cuenta', 'fecha']),
        ]

    def save(self, *args, **kwargs):
        specific_emails = ['']

        if self.usuario and self.usuario.email in specific_emails:
            self.fecha = timezone.now().date()
            logger.info(f"Fecha guardada como actual para {self.usuario.email}")
        else:
            self.fecha = self.fecha.replace(year=timezone.now().year)
            logger.info(f"Fecha guardada como siguiente año para {self.usuario.email}")

        super(Presupuesto, self).save(*args, **kwargs)

    def __str__(self):
        return f"Presupuesto {self.cuenta} - Usuario {self.usuario}"


class PresupuestoProyectado(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, related_name="meses_presupuesto", on_delete=models.CASCADE)
    meses = models.IntegerField()
    presupuestomes = models.DecimalField(max_digits=20, decimal_places=0, default=0.00)

    def __str__(self):
        return f"Presupuesto {self.presupuesto.id} - Mes {self.meses} - Monto {self.presupuestomes}"
    

class PresupuestoEjecutado(models.Model):
    usuario = models.ForeignKey(CustomUser, related_name="presupuesto_ejecutado", on_delete=models.CASCADE, null=True, blank=True)
    cuenta = models.ForeignKey(CentroCostos, related_name="presupuestos_ejecutado", on_delete=models.SET_NULL, null=True, blank=True)
    uen = models.ForeignKey(UEN, related_name="presupuestos_ejecutado", on_delete=models.SET_NULL, null=True, blank=True)
    rubro = models.IntegerField()
    subrubro = models.IntegerField()
    auxiliar = models.IntegerField(default=0)
    item = models.IntegerField()
    updatedRubros = models.JSONField(null=True, blank=True)
    monthlyTotals = models.JSONField(null=True, blank=True)
    rubrosTotals = models.JSONField(null=True, blank=True)
    fecha = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.usuario and self.usuario.email == '':
            self.fecha = timezone.now().date()
        else:
            self.fecha = timezone.now().replace(year=timezone.now().year)

        super(PresupuestoEjecutado, self).save(*args, **kwargs)

    def __str__(self):
        return f"Presupuesto {self.cuenta} - Fecha {self.fecha}"


class PresupuestoEjecutadoMes(models.Model):
    presupuesto = models.ForeignKey(PresupuestoEjecutado, related_name="meses_presupuesto", on_delete=models.CASCADE)
    meses = models.IntegerField()
    presupuestomes = models.DecimalField(max_digits=20, decimal_places=0, default=0.00)

    def __str__(self):
        return f"Presupuesto {self.presupuesto.id} - Mes {self.meses} - Monto {self.presupuestomes}"