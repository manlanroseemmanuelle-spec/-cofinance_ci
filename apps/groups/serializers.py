from rest_framework import serializers
from .models import SolidarityGroup, GroupMember, GroupeLoan


class GroupMemberSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GroupMember
        fields = ['id', 'groupe', 'client', 'client_name', 'role', 'date_adhesion', 'est_actif']
        read_only_fields = ['id', 'date_adhesion', 'client_name']

    def get_client_name(self, obj):
        return str(obj.client)


class GroupMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['groupe', 'client', 'role', 'est_actif']


class SolidarityGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SolidarityGroup
        fields = ['id', 'nom', 'type', 'centre', 'region', 'responsable', 'agent',
                  'date_creation', 'statut', 'members_count']
        read_only_fields = ['id', 'date_creation', 'members_count']

    def get_members_count(self, obj):
        return obj.members.count()


class SolidarityGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolidarityGroup
        fields = ['nom', 'type', 'centre', 'region', 'responsable', 'agent', 'statut']


class GroupeLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupeLoan
        fields = '__all__'
