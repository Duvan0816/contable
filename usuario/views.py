from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.utils import timezone

@api_view(['POST'])
@permission_classes([AllowAny])
def LoginView(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        user.last_login = timezone.now()
        user.save()
        token, created = Token.objects.get_or_create(user=user)
        
        user_type = 'admin' if user.is_active else 'user'
        return Response({
            'token': token.key,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'message': 'Login successful!',
            'userType': user_type
        }, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)
