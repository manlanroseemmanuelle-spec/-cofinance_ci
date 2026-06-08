from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ClientSerializer, ClientCreateSerializer, AgentSerializer,
    AgentCreateSerializer, ChangePasswordSerializer
)
from .models import Client, Agent
from .permissions import IsAdmin

User = get_user_model()


@extend_schema(tags=['Authentification'])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Authentification'])
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Identifiants invalides'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(tags=['Authentification'])
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema(tags=['Authentification'])
class ChangePasswordView(APIView):
    @extend_schema(request=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Ancien mot de passe incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Mot de passe modifié avec succès'})


@extend_schema(tags=['Clients'])
class ClientListView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientCreateSerializer
        return ClientSerializer


@extend_schema(tags=['Clients'])
class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ClientCreateSerializer
        return ClientSerializer


@extend_schema(tags=['Agents'])
class AgentListView(generics.ListCreateAPIView):
    queryset = Agent.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AgentCreateSerializer
        return AgentSerializer


@extend_schema(tags=['Agents'])
class AgentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Agent.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AgentCreateSerializer
        return AgentSerializer


@extend_schema(tags=['Utilisateurs'])
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


@extend_schema(tags=['Utilisateurs'])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
