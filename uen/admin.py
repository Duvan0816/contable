from django.contrib import admin
from .models import CentroCostos, Rubro, Presupuesto, SubRubro, Auxiliar, PresupuestoProyectado, PresupuestoEjecutado, PresupuestoEjecutadoMes

# Register your models here.
class CentroCostosAdmin(admin.ModelAdmin):
    # Especifica los campos que deseas mostrar en la vista de lista
    list_display = ('id','codigo', 'nombre', 'regional', 'uen', 'area')

    list_editable = ('codigo', 'nombre', 'regional', 'uen', 'area')  
    # Para permitir la edición en la vista de lista

    # Campos por los cuales se puede buscar en el panel de administración
    search_fields = ('codigo', 'nombre')

admin.site.register(CentroCostos, CentroCostosAdmin)

class PresupuestoProyectadoInline(admin.TabularInline): 
    model = PresupuestoProyectado
    extra = 0  # Number of extra blank fields to display

class PresupuestoEjecutadoMesInline(admin.TabularInline): 
    model = PresupuestoEjecutadoMes
    extra = 0  
    
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'uen', 'fecha')
    search_fields = ('usuario__first_name', 'uen__nombre', 'fecha')
    inlines = [PresupuestoProyectadoInline]
admin.site.register(Presupuesto, PresupuestoAdmin)

class PresupuestoEjecutadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'uen', 'fecha')
    search_fields = ('usuario__first_name', 'uen__nombre', 'fecha')
    inlines = [PresupuestoEjecutadoMesInline]
admin.site.register(PresupuestoEjecutado, PresupuestoEjecutadoAdmin)

class AxiliarAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre', 'subrubro')
    list_editable = ('codigo', 'nombre', 'subrubro')  
    search_fields = ('codigo', 'nombre')
    
admin.site.register(Auxiliar, AxiliarAdmin)

class SubRubroAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre', 'rubro')
    list_editable = ('codigo', 'nombre', 'rubro')  
    search_fields = ('codigo', 'nombre')
    
admin.site.register(SubRubro, SubRubroAdmin)

admin.site.register(Rubro)
