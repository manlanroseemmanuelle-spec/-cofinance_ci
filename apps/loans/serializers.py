from rest_framework import serializers
from .models import LoanApplication, AmortizationSchedule, Document, LoanStatusHistory
from apps.accounts.serializers import ClientSerializer


class LoanApplicationSerializer(serializers.ModelSerializer):
    client_details = ClientSerializer(source='client', read_only=True)

    class Meta:
        model = LoanApplication
        fields = '__all__'
        read_only_fields = ['score_eligibilite', 'date_creation', 'date_mise_a_jour']


class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['montant_demande', 'duree_mois', 'motif', 'revenu_mensuel']


class LoanStatusUpdateSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=LoanApplication.Statut.choices)
    agent = serializers.IntegerField(required=False, min_value=1)
    commentaire = serializers.CharField(required=False, allow_blank=True)

    def validate_agent(self, value):
        from apps.accounts.models import Agent
        if not Agent.objects.filter(id=value).exists():
            raise serializers.ValidationError("Cet agent n'existe pas.")
        return value


class AmortizationScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmortizationSchedule
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['date_upload']


class DocumentUploadSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=Document.TypeDocument.choices)
    fichier = serializers.FileField()


class LoanStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LoanStatusHistory
        fields = '__all__'

    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return 'Système'
