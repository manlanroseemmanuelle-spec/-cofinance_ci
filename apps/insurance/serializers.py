from rest_framework import serializers
from .models import InsuranceProduct, Policy


class InsuranceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProduct
        fields = '__all__'
        read_only_fields = ['date_creation']


class PolicySerializer(serializers.ModelSerializer):
    produit_details = InsuranceProductSerializer(source='produit', read_only=True)

    class Meta:
        model = Policy
        fields = '__all__'
        read_only_fields = ['date_souscription', 'date_fin']


class PolicyCreateSerializer(serializers.Serializer):
    produit_id = serializers.IntegerField()

    def validate_produit_id(self, value):
        from .models import InsuranceProduct
        if not InsuranceProduct.objects.filter(id=value).exists():
            raise serializers.ValidationError("Ce produit d'assurance n'existe pas.")
        return value
