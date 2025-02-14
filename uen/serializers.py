from rest_framework import serializers
from .models import Rubro, SubRubro, CentroCostos, Presupuesto, Auxiliar, PresupuestoActualizado, PresupuestoMes, PresupuestoProyectado, PresupuestoEjecutado, PresupuestoEjecutadoMes
from usuario.models import CustomUser, UEN, Regional
# from rest_framework import serializers

class AuxiliarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auxiliar
        fields = ['id', 'codigo', 'nombre']

class SubRubroSerializer(serializers.ModelSerializer):
    auxiliares = AuxiliarSerializer(many=True, read_only=True)
    
    class Meta:
        model = SubRubro
        fields = ['id', 'codigo', 'nombre', 'auxiliares']

class RubroSerializer(serializers.ModelSerializer):
    subrubros = SubRubroSerializer(many=True, read_only=True)

    class Meta:
        model = Rubro
        fields = ['id', 'codigo', 'nombre', 'subrubros']

class UENSerializer(serializers.ModelSerializer):
    class Meta:
        model = UEN
        fields = ['nombre']

class RegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regional
        fields = ['nombre']

class CentroCostosSerializer(serializers.ModelSerializer):
    uen = UENSerializer(read_only=True)
    regional = RegionalSerializer(read_only=True)
    
    class Meta:
        model = CentroCostos
        fields = ['id', 'codigo', 'nombre', 'regional', 'uen']

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email']

# Detallado  
class PresupuestoProyectadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresupuestoProyectado
        fields = ['meses', 'presupuestomes']
             
class HistorialPresupuestoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    meses_presupuesto = PresupuestoProyectadoSerializer(many=True)
    uen = UENSerializer(read_only=True)
    cuenta = serializers.SlugRelatedField(queryset=CentroCostos.objects.all(), slug_field='codigo')

    class Meta:
        model = Presupuesto
        fields = ['id', 'usuario', 'cuenta', 'uen', 'rubro', 'subrubro', 'auxiliar', 'item', 'fecha', 'updatedRubros', 'rubrosTotals', 'monthlyTotals', 'meses_presupuesto']
       
class PresupuestoSerializer(serializers.ModelSerializer):
    uen = serializers.SlugRelatedField(queryset=UEN.objects.all(), slug_field='nombre')
    meses_presupuesto = PresupuestoProyectadoSerializer(many=True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    cuenta = serializers.SerializerMethodField()

    class Meta:
        model = Presupuesto
        fields = [
            'usuario', 'cuenta', 'uen', 'rubro', 'subrubro', 'auxiliar',
            'item', 'fecha', 'updatedRubros', 'rubrosTotals', 'monthlyTotals', 'meses_presupuesto'
        ]
        
    def get_cuenta(self, obj):
        return {
            'codigo': obj.cuenta.codigo,
            'nombre': obj.cuenta.nombre,
            'regional': obj.cuenta.regional.nombre
        }       

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'GET':
            data.pop('monthlyTotals', None)
            data.pop('rubrosTotals', None)
            data.pop('updatedRubros', None)
            data.pop('item', None)
            data.pop('usuario', None)
        return data

# Ejecutado  
class PresupuestoEjecutadoMesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresupuestoEjecutadoMes
        fields = ['meses', 'presupuestomes']
             
class HistorialPresupuestoEjecutadoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    meses_presupuesto = PresupuestoEjecutadoMesSerializer(many=True)
    uen = UENSerializer(read_only=True)
    cuenta = serializers.SlugRelatedField(queryset=CentroCostos.objects.all(), slug_field='codigo')

    class Meta:
        model = PresupuestoEjecutado
        fields = ['id', 'usuario', 'cuenta', 'uen', 'rubro', 'subrubro', 'auxiliar', 'item', 'fecha', 'updatedRubros', 'rubrosTotals', 'monthlyTotals', 'meses_presupuesto']
       
class PresupuestoEjecutadoSerializer(serializers.ModelSerializer):
    uen = serializers.SlugRelatedField(queryset=UEN.objects.all(), slug_field='nombre')
    meses_presupuesto = PresupuestoEjecutadoMesSerializer(many=True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    cuenta = serializers.SerializerMethodField()

    class Meta:
        model = PresupuestoEjecutado
        fields = [
            'usuario', 'cuenta', 'uen', 'rubro', 'subrubro', 'auxiliar',
            'item', 'fecha', 'updatedRubros', 'rubrosTotals', 'monthlyTotals', 'meses_presupuesto'
        ]
        
    def get_cuenta(self, obj):
        return {
            'codigo': obj.cuenta.codigo,
            'nombre': obj.cuenta.nombre,
            'regional': obj.cuenta.regional.nombre
        }       

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'GET':
            data.pop('monthlyTotals', None)
            data.pop('rubrosTotals', None)
            data.pop('item', None)
            data.pop('usuario', None)
        return data
                

# Actualizado
class PresupuestoMesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresupuestoMes
        fields = ['meses', 'presupuestomes']

class PresupuestoActualizadoSerializer(serializers.ModelSerializer):
    uen = serializers.SlugRelatedField(queryset=UEN.objects.all(), slug_field='nombre')
    meses_presupuesto = PresupuestoMesSerializer(many=True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    cuenta = serializers.SerializerMethodField()

    class Meta:
        model = PresupuestoActualizado
        fields = [
            'usuario', 'cuenta', 'uen', 'rubro', 'subrubro', 'auxiliar',
            'item', 'fecha', 'updatedRubros', 'rubrosTotals', 'monthlyTotals', 'meses_presupuesto'
        ]
        
    def get_cuenta(self, obj):
        return {
            'codigo': obj.cuenta.codigo,
            'nombre': obj.cuenta.nombre,
            'regional': obj.cuenta.regional.nombre
        }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'GET':
            data.pop('monthlyTotals', None)
            data.pop('rubrosTotals', None)
            data.pop('item', None)
            data.pop('usuario', None)
        return data
    
class HistorialPresupuestoActualizadoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    meses_presupuesto = PresupuestoMesSerializer(many=True)
    uen = UENSerializer(read_only=True)
    cuenta = serializers.SlugRelatedField(queryset=CentroCostos.objects.all(), slug_field='codigo')

    class Meta:
        model = PresupuestoActualizado
        fields = ['id', 'usuario', 'cuenta', 'uen', 'rubro', 'subrubro', 'auxiliar', 'item', 'fecha', 'updatedRubros', 'rubrosTotals', 'monthlyTotals', 'meses_presupuesto']