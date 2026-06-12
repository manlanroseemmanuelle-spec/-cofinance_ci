from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ClientSerializer, ClientCreateSerializer, AgentSerializer,
    AgentCreateSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)
from .models import Client, Agent
from .permissions import IsAdmin

User = get_user_model()

# In-memory reset tokens (dev only — use Redis/DB in production)
_reset_tokens = {}

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
        # Send welcome email (silently ignore if email is empty)
        if user.email:
            try:
                send_mail(
                    subject='Bienvenue sur CoFinance CI',
                    message=(
                        f'Bonjour {user.get_full_name()},\n\n'
                        f'Votre compte a ete cree avec succes sur la plateforme CoFinance CI.\n'
                        f'Votre nom d\'utilisateur est : {user.username}\n\n'
                        f'Cordialement,\nL\'equipe CoFinance CI'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Authentification'])
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_scope = 'login'

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
    @extend_schema(request=ChangePasswordSerializer, responses={200: dict, 400: dict})
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


@extend_schema(tags=['Authentification'])
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        telephone = serializer.validated_data['telephone']
        try:
            user = User.objects.get(telephone=telephone)
        except User.DoesNotExist:
            return Response({'error': 'Aucun compte trouvé avec ce numéro'}, status=status.HTTP_404_NOT_FOUND)

        token = get_random_string(32)
        _reset_tokens[token] = {
            'user_id': user.id,
            'expires': timezone.now() + timedelta(hours=1),
        }
        # Send reset link by email if user has one
        if user.email:
            try:
                send_mail(
                    subject='Reinitialisation de mot de passe - CoFinance CI',
                    message=(
                        f'Bonjour {user.get_full_name()},\n\n'
                        f'Vous avez demande la reinitialisation de votre mot de passe.\n'
                        f'Utilisez ce lien pour reinitialiser votre mot de passe :\n'
                        f'{request.build_absolute_uri("/reset-password/" + token + "/")}\n\n'
                        f'Ce lien expire dans 1 heure.\n\n'
                        f'Si vous n\'etes pas a l\'origine de cette demande, ignorez ce message.\n\n'
                        f'Cordialement,\nL\'equipe CoFinance CI'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        return Response({
            'message': 'Token de réinitialisation généré',
            'token': token,
            'reset_url': f'/reset-password/{token}/',
        })


@extend_schema(tags=['Authentification'])
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        data = _reset_tokens.get(token)
        if not data:
            return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)
        if timezone.now() > data['expires']:
            del _reset_tokens[token]
            return Response({'error': 'Token expiré'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(id=data['user_id'])
        user.set_password(new_password)
        user.save()
        del _reset_tokens[token]
        return Response({'message': 'Mot de passe réinitialisé avec succès'})
