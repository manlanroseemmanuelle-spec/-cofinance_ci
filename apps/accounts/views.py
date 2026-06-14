from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ClientSerializer, ClientCreateSerializer, AgentSerializer,
    AgentCreateSerializer, ChangePasswordSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer,
    LoginHistorySerializer
)
from .models import Client, Agent, PasswordResetToken, LoginHistory
from .permissions import IsAdmin

User = get_user_model()


@extend_schema(tags=['Authentification'])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'register'

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
    queryset = Client.objects.filter(is_active=True)
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

    def perform_destroy(self, instance):
        instance.delete()


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
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


@extend_schema(tags=['Utilisateurs'])
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


@extend_schema(tags=['Authentification'])
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'forgot_password'

    @extend_schema(request=ForgotPasswordSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        telephone = serializer.validated_data['telephone']
        try:
            user = User.objects.get(telephone=telephone)
        except User.DoesNotExist:
            return Response({'error': 'Aucun compte trouvé avec ce numéro'}, status=status.HTTP_404_NOT_FOUND)

        token_str = get_random_string(48)
        PasswordResetToken.objects.create(
            user=user,
            token=token_str,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        if user.email:
            try:
                send_mail(
                    subject='Reinitialisation de mot de passe - CoFinance CI',
                    message=(
                        f'Bonjour {user.get_full_name()},\n\n'
                        f'Vous avez demande la reinitialisation de votre mot de passe.\n'
                        f'Utilisez ce lien pour reinitialiser votre mot de passe :\n'
                        f'{request.build_absolute_uri("/reset-password/" + token_str + "/")}\n\n'
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
            'message': 'Si votre compte existe, un lien de réinitialisation vous a été envoyé.',
        })


@extend_schema(tags=['Authentification'])
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'reset_password'

    @extend_schema(request=ResetPasswordSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Token invalide'}, status=status.HTTP_400_BAD_REQUEST)
        if reset_token.is_expired:
            return Response({'error': 'Token expiré'}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(new_password)
        user.save()
        reset_token.is_used = True
        reset_token.save()
        return Response({'message': 'Mot de passe réinitialisé avec succès'})


@extend_schema(tags=['Authentification'])
class LoginHistoryView(generics.ListAPIView):
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)[:20]
