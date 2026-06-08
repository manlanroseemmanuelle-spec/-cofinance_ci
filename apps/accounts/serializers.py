from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Client, Agent

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'telephone',
                  'adresse', 'region', 'photo', 'role', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                  'telephone', 'adresse', 'region', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
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
    class Meta:
        model = Client
        fields = ['profession', 'revenu_mensuel', 'date_naissance', 'numero_piece']


class AgentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Agent
        fields = '__all__'


class AgentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['matricule', 'region']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)
