from rest_framework import serializers
from .models import PaymentGatewayConfig, PaymentTransaction, MobileMoneyAccount


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayConfig
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ('api_key', 'api_secret'):
            if data.get(field):
                data[field] = '****' + data[field][-4:]
        return data


class PaymentGatewayConfigCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayConfig
        fields = '__all__'


class PaymentTransactionSerializer(serializers.ModelSerializer):
    gateway_name = serializers.CharField(source='gateway.nom', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = '__all__'


class PaymentTransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['gateway', 'loan', 'compte', 'montant', 'frais', 'devise', 'telephone', 'type', 'notes']
        extra_kwargs = {
            'montant': {'min_value': 0},
        }

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value

    def create(self, validated_data):
        import uuid
        validated_data['reference_interne'] = uuid.uuid4().hex[:12].upper()
        return super().create(validated_data)


class MobileMoneyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileMoneyAccount
        fields = '__all__'


class MobileMoneyAccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileMoneyAccount
        fields = ['operateur', 'telephone']


class PaymentInitiateSerializer(serializers.Serializer):
    gateway = serializers.IntegerField()
    telephone = serializers.CharField(max_length=20)
    montant = serializers.DecimalField(max_digits=14, decimal_places=2)
    type = serializers.ChoiceField(choices=PaymentTransaction.TYPE_CHOICES)
    loan_id = serializers.IntegerField(required=False, allow_null=True)
    compte_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_montant(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être supérieur à 0.")
        return value


class PaymentCallbackSerializer(serializers.Serializer):
    reference_interne = serializers.CharField(max_length=100)
    statut = serializers.ChoiceField(choices=['SUCCES', 'ECHEC'])
    reference_externe = serializers.CharField(required=False, allow_blank=True, default='')
    callback_data = serializers.JSONField(required=False, allow_null=True, default=None)
