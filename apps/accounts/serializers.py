from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Client, Agent, LoginHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telephone',
                  'adresse', 'region', 'photo', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    # Client-specific optional fields
    profession = serializers.CharField(required=False, allow_blank=True)
    revenu_mensuel = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    date_naissance = serializers.DateField(required=False)
    numero_piece = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                  'telephone', 'adresse', 'region', 'role',
                  'profession', 'revenu_mensuel', 'date_naissance', 'numero_piece']

    def create(self, validated_data):
        # Extract client-specific fields
        profession = validated_data.pop('profession', '')
        revenu_mensuel = validated_data.pop('revenu_mensuel', 0)
        date_naissance = validated_data.pop('date_naissance', None)
        numero_piece = validated_data.pop('numero_piece', '')
        password = validated_data.pop('password')
        role = validated_data.get('role', User.Role.CLIENT)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Auto-create Client or Agent profile based on role
        if role == User.Role.CLIENT:
            Client.objects.get_or_create(
                user=user,
                defaults={
                    'profession': profession or 'Non renseigné',
                    'revenu_mensuel': revenu_mensuel or 0,
                    'date_naissance': date_naissance or '2000-01-01',
                    'numero_piece': numero_piece or f'TMP-{user.id:06d}',
                }
            )
        elif role == User.Role.AGENT:
            Agent.objects.get_or_create(
                user=user,
                defaults={
                    'matricule': f'AGT-{user.id:06d}',
                    'region': user.region or 'Non définie',
                }
            )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Client
        fields = '__all__'


class ClientCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Client
        fields = ['user_id', 'profession', 'revenu_mensuel', 'date_naissance', 'numero_piece']

    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.get(id=validated_data.pop('user_id'))
        return Client.objects.create(user=user, **validated_data)


class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Agent
        fields = '__all__'


class AgentCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Agent
        fields = ['user_id', 'matricule', 'region']

    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.get(id=validated_data.pop('user_id'))
        return Agent.objects.create(user=user, **validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class ForgotPasswordSerializer(serializers.Serializer):
    telephone = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = '__all__'
        read_only_fields = ['id', 'date_connexion']
