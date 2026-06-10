from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import LoanApplication, AmortizationSchedule, Document, LoanStatusHistory, LoanProduct, Collateral, LoanRestructuring, GracePeriod
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
        extra_kwargs = {
            'montant_demande': {'min_value': 1},
            'duree_mois': {'min_value': 1, 'max_value': 60},
            'revenu_mensuel': {'min_value': 1},
        }


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

    def validate_fichier(self, value):
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        max_size = 5 * 1024 * 1024
        name = value.name.lower()
        if not any(name.endswith(extension) for extension in allowed_extensions):
            raise serializers.ValidationError('Formats autorisés: PDF, JPG, JPEG, PNG.')
        if value.size > max_size:
            raise serializers.ValidationError('La taille maximale autorisée est de 5 Mo.')
        return value

    def create(self, validated_data):
        return Document.objects.create(**validated_data)


class LoanStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LoanStatusHistory
        fields = '__all__'

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return 'Système'


class LoanProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanProduct
        fields = '__all__'


class CollateralSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='caution_solidaire.user.get_full_name', allow_null=True, read_only=True)

    class Meta:
        model = Collateral
        fields = '__all__'


class CollateralCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collateral
        fields = ['loan', 'type', 'description', 'valeur_estimee', 'caution_solidaire', 'fichier_justificatif']


class LoanRestructuringSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRestructuring
        fields = '__all__'
        read_only_fields = ['statut', 'date_soumission', 'date_approbation', 'approuve_par']


class LoanRestructuringActionSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=[('SOUMISE', 'Soumise'), ('APPROUVEE', 'Approuvée'), ('REJETEE', 'Rejetée')])


class GracePeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = GracePeriod
        fields = '__all__'
