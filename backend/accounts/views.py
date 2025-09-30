from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        },
    ),
    responses={200: openapi.Response('Success', examples={'application/json': {'access': 'token', 'refresh': 'token', 'role': 'ASM'}})},
)

@api_view(['POST'])
def login_view(request):
    """
    Login API using JWT tokens.
    Returns access, refresh tokens and user role.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    print(username, password)
    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'role': user.role
        })
    else:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
