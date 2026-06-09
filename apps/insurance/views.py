from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import InsuranceProduct, Policy
from .serializers import InsuranceProductSerializer, PolicySerializer, PolicyCreateSerializer
from apps.accounts.permissions import IsOwnerAdminOrAssignedAgent


@extend_schema(tags=['Assurance'])
class InsuranceProductListView(generics.ListAPIView):
    queryset = InsuranceProduct.objects.filter(est_actif=True)
    serializer_class = InsuranceProductSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['Assurance'])
class PolicyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Policy.objects.none()
        user = self.request.user
        queryset = Policy.objects.select_related('client__user', 'produit')
        if user.role == 'CLIENT':
            return queryset.filter(client=user.client_profile)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PolicyCreateSerializer
        return PolicySerializer

    def perform_create(self, serializer):
        if self.request.user.role != 'CLIENT':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les clients peuvent souscrire une assurance.")
        from django.utils import timezone
        produit = InsuranceProduct.objects.get(id=serializer.validated_data['produit_id'])
        Policy.objects.create(
            client=self.request.user.client_profile,
            produit=produit,
            date_debut=timezone.now().date(),
        )


@extend_schema(tags=['Assurance'])
class PolicyDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PolicySerializer
    permission_classes = [IsOwnerAdminOrAssignedAgent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Policy.objects.none()
        user = self.request.user
        queryset = Policy.objects.select_related('client__user', 'produit')
        if user.role == 'CLIENT':
            return queryset.filter(client=user.client_profile)
        return queryset


@extend_schema(tags=['Assurance'])
class MyPoliciesView(generics.ListAPIView):
    serializer_class = PolicySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Policy.objects.none()
        if self.request.user.role != 'CLIENT':
            return Policy.objects.none()
        return Policy.objects.filter(client=self.request.user.client_profile)
