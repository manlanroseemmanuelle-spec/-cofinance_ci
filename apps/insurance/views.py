from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import InsuranceProduct, Policy
from .serializers import InsuranceProductSerializer, PolicySerializer, PolicyCreateSerializer


@extend_schema(tags=['Assurance'])
class InsuranceProductListView(generics.ListAPIView):
    queryset = InsuranceProduct.objects.filter(est_actif=True)
    serializer_class = InsuranceProductSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['Assurance'])
class PolicyListCreateView(generics.ListCreateAPIView):
    queryset = Policy.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PolicyCreateSerializer
        return PolicySerializer

    def perform_create(self, serializer):
        produit = InsuranceProduct.objects.get(id=serializer.validated_data['produit_id'])
        from django.utils import timezone
        Policy.objects.create(
            client=self.request.user.client_profile,
            produit=produit,
            date_debut=timezone.now().date(),
        )


@extend_schema(tags=['Assurance'])
class PolicyDetailView(generics.RetrieveDestroyAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer


@extend_schema(tags=['Assurance'])
class MyPoliciesView(generics.ListAPIView):
    serializer_class = PolicySerializer

    def get_queryset(self):
        return Policy.objects.filter(client=self.request.user.client_profile)
