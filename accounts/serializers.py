# filepath: accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Review

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'type')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            type=validated_data['type']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    return user
                else:
                    raise serializers.ValidationError("Benutzerkonto ist deaktiviert.")
            else:
                raise serializers.ValidationError("Ungültige Anmeldedaten.")
        else:
            raise serializers.ValidationError("Beide Felder müssen ausgefüllt werden.")

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='id')

    class Meta:
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'email', 'type', 'file', 'location', 'tel', 'description', 'working_hours', 'created_at']
        read_only_fields = ['user_id', 'username', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'