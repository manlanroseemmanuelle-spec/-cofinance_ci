from django.db import transaction
from rest_framework import serializers
from .models import Account, JournalEntry, JournalEntryLine


class JournalEntryLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntryLine
        fields = '__all__'
        read_only_fields = ['entry']


class AccountSerializer(serializers.ModelSerializer):
    parent_code = serializers.CharField(source='parent.code', read_only=True, allow_null=True)

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['code']


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class JournalEntryLineCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'sens', 'montant', 'libelle']


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True, read_only=True)
    total_debit = serializers.SerializerMethodField()
    total_credit = serializers.SerializerMethodField()

    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = ['reference', 'est_validee', 'validee_par', 'date_validation', 'date_creation']

    @staticmethod
    def _compute_totals(obj):
        lines = getattr(obj, '_prefetched_lines', None)
        if lines is None:
            lines = obj.lines.all()
        total_debit = sum(line.montant for line in lines if line.sens == 'DEBIT')
        total_credit = sum(line.montant for line in lines if line.sens == 'CREDIT')
        return total_debit, total_credit

    def get_total_debit(self, obj):
        total, _ = self._compute_totals(obj)
        return total

    def get_total_credit(self, obj):
        _, total = self._compute_totals(obj)
        return total


class JournalEntryCreateSerializer(serializers.ModelSerializer):
    lines = JournalEntryLineCreateSerializer(many=True)

    class Meta:
        model = JournalEntry
        fields = ['journal', 'date_ecriture', 'libelle', 'loan', 'client', 'agent', 'lines']

    def validate_lines(self, lines):
        if not lines:
            raise serializers.ValidationError('Au moins une ligne est requise.')
        for line in lines:
            if line['montant'] <= 0:
                raise serializers.ValidationError('Chaque montant doit être supérieur à zéro.')
        total_debit = sum(l['montant'] for l in lines if l['sens'] == 'DEBIT')
        total_credit = sum(l['montant'] for l in lines if l['sens'] == 'CREDIT')
        if total_debit != total_credit:
            raise serializers.ValidationError(
                f'Le total doit être équilibré (Débit: {total_debit}, Crédit: {total_credit}).'
            )
        return lines

    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        validated_data['reference'] = JournalEntry.generer_reference()
        entry = JournalEntry.objects.create(**validated_data)
        for line_data in lines_data:
            JournalEntryLine.objects.create(entry=entry, **line_data)
        return entry


class JournalEntryValidationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['valider'])

    def validate_action(self, value):
        entry = self.context['entry']
        if entry.est_validee:
            raise serializers.ValidationError('Cette écriture est déjà validée.')
        return value
