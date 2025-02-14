# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RubroViewSet, SubRubroViewSet, CentroCostosListView, PresupuestoViewSet, InformeDetalladoPresupuestoViewSet, AuxiliarViewSet, BatchUpdatePresupuestoView, PresupuestoActualizadoViewSet, HistorialPresupuestoActualizadoViewSet, HistorialPresupuestoViewSet, PresupuestoEjecutadoViewSet, HistorialPresupuestoEjecuatdoViewSet, InformePresupuestoEjecutadoViewSet
# from . import views

router = DefaultRouter()
router.register(r'rubros', RubroViewSet)
router.register(r'subrubros', SubRubroViewSet)
router.register(r'auxiliares', AuxiliarViewSet)
router.register(r'CentroCostos', CentroCostosListView)
router.register(r'presupuestos', PresupuestoViewSet, basename='presupuesto')
router.register(r'presupuestosActualizado', BatchUpdatePresupuestoView, basename='presupuestosActualizado')
router.register(r'Actualizado', PresupuestoActualizadoViewSet, basename='Actualizado')
router.register(r'HistorialPresupuestoActualizado', HistorialPresupuestoActualizadoViewSet, basename='historialPresupuestoActualizado')
router.register(r'HistorialPresupuesto', HistorialPresupuestoViewSet, basename='historial-presupuesto')
router.register(r'InformeDetalladoPresupuesto', InformeDetalladoPresupuestoViewSet, basename='Informe-Detallado-presupuesto')
router.register(r'presupuestoEjecutado', PresupuestoEjecutadoViewSet, basename='presupuestoEjecutado')
router.register(r'HistorialPresupuestoEjecutado', HistorialPresupuestoEjecuatdoViewSet, basename='HistorialPresupuestoEjecutado')
router.register(r'InformePresupuestoEjecutado', InformePresupuestoEjecutadoViewSet, basename='InformePresupuestoEjecutado')

urlpatterns = [
    path('', include(router.urls)),
    # path('save-presupuesto-total/', views.save_presupuesto_total, name='save-presupuesto-total'),
]