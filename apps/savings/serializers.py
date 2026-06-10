import uuid

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import SavingsProduct, SavingsAccount, SavingsTransaction
from apps.accounts.serializers import ClientSerializer


class SavingsProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsProduct
        fields = '__all__'


class SavingsAccountSerializer(serializers.ModelSerializer):
    client_details = ClientSerializer(source='client', read_only=True)

    class Meta:
        model = SavingsAccount
        fields = '__all__'
        read_only_fields = ['numero_compte', 'solde', 'date_ouverture']


class SavingsAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsAccount
        fields = ['client', 'produit']

    def create(self, validated_data):
        validated_data['numero_compte'] = f"CMP-{uuid.uuid4().hex[:6].upper()}"
        return super().create(validated_data)


class SavingsTransactionSerializer(serializers.ModelSerializer):
    agent_name = serializers.SerializerMethodField()

    class Meta:
        model = SavingsTransaction
        fields = '__all__'
        read_only_fields = ['reference', 'solde_avant', 'solde_apres', 'date_transaction']

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_agent_name(self, obj):
        if obj.agent:
            return obj.agent.user.get_full_name() or obj.agent.user.username
        return None


class SavingsTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsTransaction
        fields = ['compte', 'type', 'montant', 'agent', 'notes']

    def validate(self, attrs):
        compte = attrs['compte']
        type_txn = attrs['type']
        montant = attrs['montant']

        solde_avant = compte.solde

        if type_txn in ('RETRAIT', 'FRAIS') and montant > solde_avant:
            raise serializers.ValidationError(
                {"montant": "Solde insuffisant pour effectuer cette opération."}
            )

        if type_txn in ('RETRAIT', 'FRAIS'):
            solde_apres = solde_avant - montant
        else:
            solde_apres = solde_avant + montant

        attrs['solde_avant'] = solde_avant
        attrs['solde_apres'] = solde_apres
        return attrs

    def create(self, validated_data):
        compte = validated_data['compte']
        solde_apres = validated_data.pop('solde_apres')
        validated_data['solde_avant'] = validated_data.pop('solde_avant')
        instance = super().create(validated_data)
        compte.solde = solde_apres
        compte.save(update_fields=['solde'])
        return instance
