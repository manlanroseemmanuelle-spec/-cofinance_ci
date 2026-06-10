from rest_framework import serializers
from .models import RegulatoryReport, PrudentialRatio, LoanClassification, DeclarationSuspicion


class RegulatoryReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryReport
        fields = '__all__'
        read_only_fields = ['id', 'date_generation', 'statut', 'generated_by']


class RegulatoryReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryReport
        fields = ['type', 'periode', 'contenu']

    def create(self, validated_data):
        validated_data['generated_by'] = self.context['request'].user
        return super().create(validated_data)


class PrudentialRatioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrudentialRatio
        fields = '__all__'
        read_only_fields = ['id', 'date_calcul']


class PrudentialRatioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrudentialRatio
        fields = ['code', 'nom', 'valeur_actuelle', 'statut']


class LoanClassificationSerializer(serializers.ModelSerializer):
    loan_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LoanClassification
        fields = '__all__'

    def get_loan_details(self, obj):
        from apps.loans.serializers import LoanApplicationSerializer
        return LoanApplicationSerializer(obj.loan).data if obj.loan else None


class DeclarationSuspicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeclarationSuspicion
        fields = '__all__'
        read_only_fields = ['id', 'date_declaration', 'reference', 'declared_by']


class DeclarationSuspicionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeclarationSuspicion
        fields = ['client', 'transaction', 'montant', 'motifs', 'date_faits']

    def create(self, validated_data):
        import uuid
        validated_data['reference'] = f"DS-{uuid.uuid4().hex[:8].upper()}"
        validated_data['declared_by'] = self.context['request'].user
        return super().create(validated_data)
