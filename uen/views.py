from rest_framework import status, viewsets
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Rubro, SubRubro, CentroCostos, Presupuesto, Auxiliar, PresupuestoActualizado, PresupuestoMes, PresupuestoProyectado, PresupuestoEjecutado, PresupuestoEjecutadoMes
from .serializers import RubroSerializer, SubRubroSerializer, CentroCostosSerializer, PresupuestoSerializer, HistorialPresupuestoSerializer, AuxiliarSerializer, PresupuestoActualizadoSerializer, HistorialPresupuestoActualizadoSerializer, HistorialPresupuestoEjecutadoSerializer, PresupuestoEjecutadoSerializer
from django.core.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
import logging
from django.db import IntegrityError
from django.db.models import CharField, F, Func, Max
from django.db.models.functions import Cast, ExtractYear

logger = logging.getLogger(__name__)

class BatchUpdatePresupuestoView(viewsets.ModelViewSet):
    queryset = PresupuestoActualizado.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PresupuestoActualizadoSerializer

    @action(detail=False, methods=['patch'], url_path='batch-update')
    @transaction.atomic
    def update_batch(self, request):

        # Validate that the input is a list
        if not isinstance(request.data, list):
            logger.error("Invalid data format: Expected a list")
            return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize result variables
        valid_updates, new_data, invalid_data = [], [], []
        presupuesto_mes_data_to_create = []
        presupuesto_mes_data_to_update = []
        instance_map = {}

        # Query only IDs in request data
        ids = [item.get('id') for item in request.data if 'id' in item]
        instances = PresupuestoActualizado.objects.filter(id__in=ids)
        instance_map = {instance.id: instance for instance in instances}

        # Group data by unique keys to prevent duplication
        grouped_data = {}
        # Group data by unique combinations
        for data in request.data:
            try:
                instance_id = data.get('id')

                # Convert `cuenta` to corresponding `CentroCostos` ID
                if 'cuenta' in data:
                    try:
                        centro_costos = CentroCostos.objects.get(codigo=data['cuenta'])
                        data['cuenta'] = centro_costos.id
                        logger.info(f"Assigned CentroCostos ID {centro_costos.id} to cuenta.")
                    except CentroCostos.DoesNotExist:
                        invalid_data.append({"cuenta": [f"Cuenta '{data['cuenta']}' not found in CentroCostos.codigo"]})
                        continue

                group_key = (data.get('usuario'), data.get('cuenta'), data.get('uen'), data.get('rubro'), data.get('subrubro'), data.get('auxiliar'), data.get('item'))

                if group_key not in grouped_data:
                    grouped_data[group_key] = {
                        'data': data,
                        'mesesData': data.get('mesesData', []),
                        'instance_id': instance_id
                    }
                else:
                    grouped_data[group_key]['mesesData'].extend(data.get('mesesData', []))

            except ValidationError as e:
                logger.error(f"Validation error for cuenta in data: {data}, error: {str(e)}")
                invalid_data.append({"cuenta": [str(e)]})

        logger.info(f"Grouped data: {grouped_data}")

        for group_key, group_value in grouped_data.items():
            data = group_value['data']
            mesesData = group_value['mesesData']
            instance_id = group_value['instance_id']

            # Check if the instance exists and serialize data
            instance = instance_map.get(instance_id)
            serializer = self.get_serializer(instance, data=data, partial=True)

            if serializer.is_valid():
                if instance:
                    instance.cuenta_id = data['cuenta']  # Direct assignment for cuenta
                    valid_updates.append(serializer)
                else:
                    validated_data = serializer.validated_data
                    new_instance = PresupuestoActualizado(**validated_data)
                    new_instance.cuenta_id = data['cuenta']  # Direct assignment for cuenta
                    new_instance.save()
                    new_data.append(new_instance)
                    grouped_data[group_key]['instance'] = new_instance

                # Handle `mesesData`
                for meses_entry in mesesData:
                    meses = meses_entry.get('meses')
                    presupuestomes = meses_entry.get('presupuestomes')
                    presupuesto_instance = instance or new_instance
                    
                    if meses is not None and presupuestomes is not None:
                        existing_presupuesto_mes = PresupuestoMes.objects.filter(
                            presupuesto=presupuesto_instance,
                            meses=meses
                        ).first()

                        if existing_presupuesto_mes:
                            existing_presupuesto_mes.presupuestomes = presupuestomes
                            presupuesto_mes_data_to_update.append(existing_presupuesto_mes)
                        else:
                            presupuesto_mes_data_to_create.append(
                                PresupuestoMes(
                                    presupuesto=presupuesto_instance,
                                    meses=meses,
                                    presupuestomes=presupuestomes
                                )
                            )
            else:
                invalid_data.append(serializer.errors)

        # Save valid updates
        try:
            for ser in valid_updates:
                ser.save()
                logger.info(f"Updated instance: {ser.instance.id}")
        except IntegrityError as e:
            logger.error(f"Error updating instances: {str(e)}")
            return Response({"error": "Error updating records", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save new instances
        try:
            for new_instance in new_data:
                new_instance.save()
                logger.info(f"Created new instance: {new_instance.id}")
        except ValidationError as e:
            logger.error(f"Error creating new records: {str(e)}")
            return Response({"error": "Error creating records", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Bulk save for new `PresupuestoMes` entries
        if presupuesto_mes_data_to_create:
            try:
                PresupuestoMes.objects.bulk_create(presupuesto_mes_data_to_create, ignore_conflicts=True)
                logger.info(f"Created {len(presupuesto_mes_data_to_create)} new PresupuestoMes entries")
            except ValidationError as e:
                logger.error(f"Error saving new PresupuestoMes data: {str(e)}")
                return Response({"error": "Error saving new PresupuestoMes data", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Bulk save for updated `PresupuPresupuestoMesestoProyectado` entries
        if presupuesto_mes_data_to_update:
            try:
                PresupuestoMes.objects.bulk_update(presupuesto_mes_data_to_update, ['presupuestomes'])
                logger.info(f"Updated {len(presupuesto_mes_data_to_update)} PresupuestoMes entries")
            except ValidationError as e:
                logger.error(f"Error updating PresupuestoMes data: {str(e)}")
                return Response({"error": "Error updating PresupuestoMes data", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "Batch update successful",
            "updated": len(valid_updates),
            "created": len(new_data),
            "invalid_data": invalid_data
        }, status=status.HTTP_200_OK)

class RubroViewSet(viewsets.ModelViewSet):
    queryset = Rubro.objects.all()
    serializer_class = RubroSerializer
    permission_classes = [IsAuthenticated]

class SubRubroViewSet(viewsets.ModelViewSet):
    queryset = SubRubro.objects.all()
    serializer_class = SubRubroSerializer
    permission_classes = [IsAuthenticated]

class AuxiliarViewSet(viewsets.ModelViewSet):
    queryset = Auxiliar.objects.all()
    serializer_class = AuxiliarSerializer
    permission_classes = [IsAuthenticated]

class CentroCostosListView(viewsets.ModelViewSet):
    serializer_class = CentroCostosSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CentroCostos.objects.none()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.uen.exists():
            queryset = CentroCostos.objects.filter(uen__in=user.uen.all())
            return queryset
        return CentroCostos.objects.none()

    def list(self, request, *args, **kwargs):
        # token = get_token(request)
        original_response = super().list(request, *args, **kwargs)
        response_data = original_response.data

        user_id = request.user.id

        if isinstance(response_data, dict):
            response_data['user_id'] = user_id
        elif isinstance(response_data, list):
            response_data = {
                'user_id': user_id,
                'results': response_data
            }
        else:
            response_data = {
                'user_id': user_id,
                'results': []
            }

        return Response(response_data, status=status.HTTP_200_OK)

class PresupuestoViewSet(viewsets.ModelViewSet):
    # queryset = Presupuesto.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PresupuestoSerializer
    def get_queryset(self):
        """
        Sobrescribe el método get_queryset para filtrar por el usuario autenticado.
        """
        return Presupuesto.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['patch'], url_path='batch-update')
    @transaction.atomic
    def update_batch(self, request):
        logger.info(f"Processing data: {request.data}")

        if not isinstance(request.data, list):
            logger.error("Invalid data format: Expected a list")
            return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

        # Get IDs of existing records
        ids = [item.get('id') for item in request.data if 'id' in item]
        instances = Presupuesto.objects.filter(usuario=self.request.user, id__in=ids)
        instance_map = {instance.id: instance for instance in instances}

        valid_updates, new_data, invalid_data = [], [], []
        presupuesto_mes_data_to_create = []
        presupuesto_mes_data_to_update = []

        grouped_data = {}

        # Group data by unique combinations
        for data in request.data:
            try:
                instance_id = data.get('id')

                # Convert `cuenta` to corresponding `CentroCostos` ID
                if 'cuenta' in data:
                    try:
                        centro_costos = CentroCostos.objects.get(codigo=data['cuenta'])
                        data['cuenta'] = centro_costos.id
                        logger.info(f"Assigned CentroCostos ID {centro_costos.id} to cuenta.")
                    except CentroCostos.DoesNotExist:
                        logger.warning(f"Cuenta '{data['cuenta']}' not found in CentroCostos.codigo")
                        invalid_data.append({"cuenta": [f"Cuenta '{data['cuenta']}' not found in CentroCostos.codigo"]})
                        continue

                group_key = (data.get('id'), data.get('cuenta'), data.get('uen'), data.get('rubro'), data.get('subrubro'), data.get('auxiliar'), data.get('item'))

                if group_key not in grouped_data:
                    grouped_data[group_key] = {
                        'data': data,
                        'mesesData': data.get('mesesData', []),
                        'instance_id': instance_id
                    }
                else:
                    grouped_data[group_key]['mesesData'].extend(data.get('mesesData', []))

            except ValidationError as e:
                logger.error(f"Validation error for cuenta in data: {data}, error: {str(e)}")
                invalid_data.append({"cuenta": [str(e)]})

        logger.info(f"Grouped data: {grouped_data}")

        for group_key, group_value in grouped_data.items():
            data = group_value['data']
            mesesData = group_value['mesesData']
            instance_id = group_value['instance_id']

            # Check if the instance exists and serialize data
            instance = instance_map.get(instance_id)
            serializer = self.get_serializer(instance, data=data, partial=True)

            if serializer.is_valid():
                if instance:
                    instance.cuenta_id = data['cuenta']  # Direct assignment for cuenta
                    valid_updates.append(serializer)
                else:
                    validated_data = serializer.validated_data
                    new_instance = Presupuesto(**validated_data)
                    new_instance.cuenta_id = data['cuenta']  # Direct assignment for cuenta
                    new_instance.save()
                    new_data.append(new_instance)
                    grouped_data[group_key]['instance'] = new_instance

                # Handle `mesesData` for either updates or new entries
                for meses_entry in mesesData:
                    meses = meses_entry.get('meses')
                    presupuestomes = meses_entry.get('presupuestomes')
                    presupuesto_instance = instance or new_instance

                    if meses is not None and presupuestomes is not None:
                        # Check if the month exists
                        existing_presupuesto_mes = PresupuestoProyectado.objects.filter(
                            presupuesto=presupuesto_instance,
                            meses=meses
                        ).first()

                        if existing_presupuesto_mes:
                            # Add to update list if the month already exists
                            existing_presupuesto_mes.presupuestomes = presupuestomes
                            presupuesto_mes_data_to_update.append(existing_presupuesto_mes)
                        else:
                            # Add to create list if it's a new month entry
                            presupuesto_mes_data_to_create.append(
                                PresupuestoProyectado(
                                    presupuesto=presupuesto_instance,
                                    meses=meses,
                                    presupuestomes=presupuestomes
                                )
                            )
            else:
                logger.error(f"Validation failed for data: {data}, errors: {serializer.errors}")
                invalid_data.append(serializer.errors)

        logger.info(f"Total valid updates: {len(valid_updates)}, new entries: {len(new_data)}, invalid entries: {len(invalid_data)}")

        # Save valid updates
        try:
            for ser in valid_updates:
                ser.save()
                logger.info(f"Updated instance: {ser.instance.id}")
        except IntegrityError as e:
            logger.error(f"Error updating instances: {str(e)}")
            return Response({"error": "Error updating records", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Save new instances
        try:
            for new_instance in new_data:
                new_instance.save()
                logger.info(f"Created new instance: {new_instance.id}")
        except ValidationError as e:
            logger.error(f"Error creating new records: {str(e)}")
            return Response({"error": "Error creating records", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Bulk save for new `PresupuestoProyectado` entries
        if presupuesto_mes_data_to_create:
            try:
                PresupuestoProyectado.objects.bulk_create(presupuesto_mes_data_to_create, ignore_conflicts=True)
                logger.info(f"Created {len(presupuesto_mes_data_to_create)} new PresupuestoProyectado entries")
            except ValidationError as e:
                logger.error(f"Error saving new PresupuestoProyectado data: {str(e)}")
                return Response({"error": "Error saving new PresupuestoProyectado data", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Bulk save for updated `PresupuestoProyectado` entries
        if presupuesto_mes_data_to_update:
            try:
                PresupuestoProyectado.objects.bulk_update(presupuesto_mes_data_to_update, ['presupuestomes'])
                logger.info(f"Updated {len(presupuesto_mes_data_to_update)} PresupuestoProyectado entries")
            except ValidationError as e:
                logger.error(f"Error updating PresupuestoProyectado data: {str(e)}")
                return Response({"error": "Error updating PresupuestoProyectado data", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "Batch update successful",
            "updated": len(valid_updates),
            "created": len(new_data),
            "invalid_data": invalid_data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='batch-delete')
    def delete_batch(self, request):
        if not isinstance(request.data, list):
            return Response({"error": "Formato de datos inválido"}, status=status.HTTP_400_BAD_REQUEST)

        ids = [item.get('id') for item in request.data if 'id' in item]
        if not ids:
            return Response({"error": "No se proporcionaron IDs válidos"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si los registros existen
        existentes = Presupuesto.objects.filter(id__in=ids).values_list('id', flat=True)

        if not existentes:
            return Response({"error": "No se encontraron registros para eliminar"}, status=status.HTTP_404_NOT_FOUND)

        try:
            deleted_count, _ = Presupuesto.objects.filter(id__in=existentes).delete()
            print(f"Registros eliminados: {deleted_count}")
            return Response({"status": "Eliminación exitosa", "deleted_count": deleted_count, "deleted_ids": list(existentes)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Error al eliminar: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class PresupuestoEjecutadoViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PresupuestoEjecutadoSerializer

    def get_queryset(self):
        return PresupuestoEjecutado.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['patch'], url_path='batch-update')
    @transaction.atomic
    def update_batch(self, request):
        logger.info(f"Processing data: {len(request.data)} items")

        if not isinstance(request.data, list):
            return Response({"error": "Invalid data format"}, status=status.HTTP_400_BAD_REQUEST)

        # Get IDs of existing records
        ids = [item.get('id') for item in request.data if 'id' in item]
        instances = PresupuestoEjecutado.objects.filter(id__in=ids)
        instance_map = {instance.id: instance for instance in instances}

        # Obtener todos los CentroCostos de una vez
        cuenta_codigos = {item['cuenta'] for item in request.data if 'cuenta' in item}
        centro_costos_map = {cc.codigo: cc.id for cc in CentroCostos.objects.filter(codigo__in=cuenta_codigos)}

        valid_updates, new_data, invalid_data = [], [], []
        presupuesto_mes_data_to_create, presupuesto_mes_data_to_update = [], []

        grouped_data = {}

        # Group data by unique combinations
        for data in request.data:
            try:
                instance_id = data.get('id')

                # Convert `cuenta` to corresponding `CentroCostos` ID
                if 'cuenta' in data:
                    cuenta_codigo = data['cuenta']
                    if cuenta_codigo in centro_costos_map:
                        data['cuenta'] = centro_costos_map[cuenta_codigo]
                    else:
                        invalid_data.append({"cuenta": [f"Cuenta '{cuenta_codigo}' not found"]})
                        continue

                group_key = (instance_id, data.get('cuenta'), data.get('uen'), data.get('rubro'),
                             data.get('subrubro'), data.get('auxiliar'), data.get('item'))
                
                if group_key not in grouped_data:
                    grouped_data[group_key] = {
                        'data': data,
                        'mesesData': data.get('mesesData', []),
                        'instance_id': instance_id
                    }
                else:
                    grouped_data[group_key]['mesesData'].extend(data.get('mesesData', []))

            except Exception as e:
                    logger.error(f"Error processing data: {str(e)}")
                    invalid_data.append({"error": str(e)})

        logger.info(f"Grouped {len(grouped_data)} unique items for batch processing.")


        for group_key, group_value in grouped_data.items():
            data, mesesData = group_value['data'], group_value['mesesData']
            instance = instance_map.get(data.get('id'))

            serializer = self.get_serializer(instance, data=data, partial=True)

            if serializer.is_valid():
                if instance:
                    instance.cuenta_id = data['cuenta']  # Direct assignment for cuenta
                    valid_updates.append(serializer)
                else:
                    validated_data = serializer.validated_data
                    new_instance = PresupuestoEjecutado(**validated_data)
                    new_instance.cuenta_id = data['cuenta']  # Direct assignment for cuenta
                    new_instance.save()
                    new_data.append(new_instance)

                # Handle `mesesData` for either updates or new entries
                for meses_entry in mesesData:
                    meses, presupuestomes = meses_entry.get('meses'), meses_entry.get('presupuestomes')
                    if meses is None or presupuestomes is None:
                        continue

                    presupuesto_instance = instance or new_instance

                    existing_presupuesto_mes = PresupuestoEjecutadoMes.objects.filter(
                        presupuesto=presupuesto_instance, meses=meses
                    ).first()

                    if existing_presupuesto_mes:
                        existing_presupuesto_mes.presupuestomes = presupuestomes
                        presupuesto_mes_data_to_update.append(existing_presupuesto_mes)
                    else:
                        presupuesto_mes_data_to_create.append(
                            PresupuestoEjecutadoMes(presupuesto=presupuesto_instance, meses=meses, presupuestomes=presupuestomes)
                        )
            else:
                invalid_data.append(serializer.errors)

        # Guardar actualizaciones en lotes
        try:
            if valid_updates:
                PresupuestoEjecutado.objects.bulk_update(valid_updates, ['cuenta_id'])
                logger.info(f"Updated {len(valid_updates)} PresupuestoEjecutado records")

            if new_data:
                PresupuestoEjecutado.objects.bulk_create(new_data, ignore_conflicts=True)
                logger.info(f"Created {len(new_data)} new PresupuestoEjecutado records")

            if presupuesto_mes_data_to_create:
                PresupuestoEjecutadoMes.objects.bulk_create(presupuesto_mes_data_to_create, ignore_conflicts=True)
                logger.info(f"Created {len(presupuesto_mes_data_to_create)} new PresupuestoEjecutadoMes records")

            if presupuesto_mes_data_to_update:
                PresupuestoEjecutadoMes.objects.bulk_update(presupuesto_mes_data_to_update, ['presupuestomes'])
                logger.info(f"Updated {len(presupuesto_mes_data_to_update)} PresupuestoEjecutadoMes records")

        except IntegrityError as e:
            logger.error(f"Database error: {str(e)}")
            return Response({"error": "Error processing records", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "Batch update successful",
            "updated": len(valid_updates),
            "created": len(new_data),
            "invalid_data": invalid_data
        }, status=status.HTTP_200_OK)

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000 
    page_size_query_param = 'page_size'
    max_page_size = 25000

class HistorialPresupuestoViewSet(viewsets.ModelViewSet):
    queryset = Presupuesto.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = HistorialPresupuestoSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        try:
            user = self.request.user
            if user.is_authenticated:
                if user.email in ['analistadecontrol@inacar.com', 'nramirez@inacar.com']:
                    return Presupuesto.objects.select_related('usuario', 'cuenta', 'uen').order_by('id')
                elif user.email == 'mauriciosilva@inacar.com':
                    return Presupuesto.objects.filter(uen__nombre="Constructora").select_related('usuario', 'cuenta', 'uen').order_by('id')
                return Presupuesto.objects.filter(usuario=user).select_related('usuario', 'cuenta', 'uen').order_by('id')

            return Presupuesto.objects.none()
        except Exception as e:
            logger.error(f"Error fetching presupuesto data: {e}")
            return Presupuesto.objects.none()

class HistorialPresupuestoEjecuatdoViewSet(viewsets.ModelViewSet):
    queryset = PresupuestoEjecutado.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = HistorialPresupuestoEjecutadoSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        try:
            user = self.request.user
            if user.is_authenticated:
                # Check if the user's email is the specified one with access to all data
                if user.email in ['analistadecontrol@inacar.com', 'nramirez@inacar.com']:
                    return PresupuestoEjecutado.objects.select_related('usuario', 'cuenta', 'uen').order_by('id')

                # Access for 'mauriciosilva@inacar.com' to records of uen 'Constructora'
                elif user.email == 'mauriciosilva@inacar.com':
                    return PresupuestoEjecutado.objects.filter(uen__nombre="Constructora").select_related('usuario', 'cuenta', 'uen').order_by('id')

                # For other users, return their specific presupuesto records
                return PresupuestoEjecutado.objects.filter(usuario=user).select_related('usuario', 'cuenta', 'uen').order_by('id')

            return PresupuestoEjecutado.objects.none()  # Return an empty queryset for unauthenticated users
        except Exception as e:
            logger.error(f"Error fetching presupuesto data: {e}")
            return PresupuestoEjecutado.objects.none()  # Return an empty queryset in case of error

class HistorialPresupuestoActualizadoViewSet(viewsets.ModelViewSet):
    queryset = PresupuestoActualizado.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = HistorialPresupuestoActualizadoSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        try:
            user = self.request.user
            if user.is_authenticated:
                # Check if the user's email is the specified one with access to all data
                if user.email in ['analistadecontrol@inacar.com', 'nramirez@inacar.com']:
                    return PresupuestoActualizado.objects.select_related('usuario', 'cuenta', 'uen').order_by('id')

                # Access for 'mauriciosilva@inacar.com' to records of uen 'Constructora'
                elif user.email == 'mauriciosilva@inacar.com':
                    return PresupuestoActualizado.objects.filter(uen__nombre="Constructora").select_related('usuario', 'cuenta', 'uen').order_by('id')

                # For other users, return their specific presupuesto records
                return PresupuestoActualizado.objects.filter(usuario=user).select_related('usuario', 'cuenta', 'uen').order_by('id')

            return PresupuestoActualizado.objects.none()
        except Exception as e:
            logger.error(f"Error fetching presupuesto data: {e}")
            return PresupuestoActualizado.objects.none()

class LargeResultsSetPaginationes(PageNumberPagination):
    page_size = 3000 
    page_size_query_param = 'page_size'
    max_page_size = 35000

class InformeDetalladoPresupuestoViewSet(viewsets.ModelViewSet):
    queryset = Presupuesto.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PresupuestoSerializer
    pagination_class = LargeResultsSetPaginationes

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PresupuestoSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        year = self.request.query_params.get('year', 2025)
        return (
        Presupuesto.objects.select_related('uen', 'cuenta__regional')
        .only('id', 'uen__nombre', 'cuenta__regional__nombre', 'fecha')
        .filter(fecha__year=year)
        .order_by('uen__nombre', 'cuenta__regional__nombre')
    )

class InformePresupuestoEjecutadoViewSet(viewsets.ModelViewSet):
    queryset = PresupuestoEjecutado.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PresupuestoEjecutadoSerializer
    pagination_class = LargeResultsSetPaginationes

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PresupuestoEjecutadoSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        # year = self.request.query_params.get('year', 2026)
        return (
        PresupuestoEjecutado.objects.select_related('uen', 'cuenta__regional')
        .only('id', 'uen__nombre', 'cuenta__regional__nombre', 'fecha')
        # .filter(fecha__year=year)
        .order_by('uen__nombre', 'cuenta__regional__nombre')
    )

class PresupuestoActualizadoViewSet(viewsets.ModelViewSet):
    queryset = PresupuestoActualizado.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PresupuestoActualizadoSerializer
    pagination_class = LargeResultsSetPaginationes

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PresupuestoActualizadoSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        # year = self.request.query_params.get('year', 2025)
        return (
        PresupuestoActualizado.objects.select_related('uen', 'cuenta__regional')
        .only('id', 'uen__nombre', 'cuenta__regional__nombre', 'fecha')
        # .filter(fecha__year=year)
        .order_by('uen__nombre', 'cuenta__regional__nombre')
    )
