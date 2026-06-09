from rest_framework import serializers
from .models import Repayment


class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = '__all__'
        read_only_fields = ['date_paiement', 'reference', 'penalite']


class RepaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = ['loan', 'amortization', 'montant', 'mode_paiement', 'notes']
        extra_kwargs = {
            'montant': {'min_value': 1},
        }

    def validate(self, attrs):
        amortization = attrs.get('amortization')
        loan = attrs.get('loan')
        if amortization and amortization.loan_id != loan.id:
            raise serializers.ValidationError({'amortization': "Cette échéance n'appartient pas au prêt indiqué."})
        return attrs
