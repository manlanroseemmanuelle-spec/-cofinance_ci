from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from .models import SolidarityGroup, GroupMember, GroupeLoan
from .serializers import (
    SolidarityGroupSerializer,
    SolidarityGroupCreateSerializer,
    GroupMemberSerializer,
    GroupMemberCreateSerializer,
    GroupeLoanSerializer,
)
from apps.accounts.permissions import IsAdmin, IsAgent, IsAdminOrAgent


@extend_schema(tags=['Groupes'])
class SolidarityGroupListCreateView(generics.ListCreateAPIView):
    queryset = SolidarityGroup.objects.select_related('responsable', 'agent').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SolidarityGroupCreateSerializer
        return SolidarityGroupSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permission() for permission in [IsAdminOrAgent]]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'AGENT':
            qs = qs.filter(agent__user=user)
        return qs


@extend_schema(tags=['Groupes'])
class SolidarityGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SolidarityGroup.objects.select_related('responsable', 'agent').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return SolidarityGroupCreateSerializer
        return SolidarityGroupSerializer


@extend_schema(tags=['Groupes'])
class GroupMemberListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupMemberCreateSerializer
        return GroupMemberSerializer

    def get_queryset(self):
        return GroupMember.objects.filter(groupe_id=self.kwargs['group_id']).select_related('client', 'client__user', 'groupe')

    def perform_create(self, serializer):
        serializer.save(groupe_id=self.kwargs['group_id'])


@extend_schema(tags=['Groupes'])
class GroupMemberRemoveView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GroupMember.objects.filter(groupe_id=self.kwargs['group_id'])


@extend_schema(tags=['Groupes'])
class MyGroupsView(generics.ListAPIView):
    serializer_class = SolidarityGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SolidarityGroup.objects.filter(
            members__client__user=self.request.user
        ).select_related('responsable', 'agent').distinct()


@extend_schema(tags=['Groupes'])
class AgentGroupsView(generics.ListAPIView):
    serializer_class = SolidarityGroupSerializer
    permission_classes = [IsAgent]

    def get_queryset(self):
        return SolidarityGroup.objects.filter(
            agent__user=self.request.user
        ).select_related('responsable', 'agent')


@extend_schema(tags=['Groupes'])
class GroupeLoanListView(generics.ListAPIView):
    serializer_class = GroupeLoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GroupeLoan.objects.filter(
            groupe_id=self.kwargs['group_id']
        ).select_related('groupe', 'loan')
