from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Review

# 👇 Neuer verschachtelter User-Serializer für Kunden-/Business-Profil-Listen
class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name']


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


# 👇 Haupt-User-Detail-Serializer (z. B. für eigenes Profil)
class UserSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField(source='id', read_only=True)  # Alias für `id`

    class Meta:
        model = User
        fields = [
            'pk', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['pk', 'username', 'email', 'created_at']
        extra_kwargs = {
            'first_name': {'required': False, 'allow_null': True},
            'last_name': {'required': False, 'allow_null': True},
            'file': {'required': False, 'allow_null': True},
            'location': {'required': False, 'allow_null': True},
            'tel': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'working_hours': {'required': False, 'allow_null': True},
        }

# 👇 Kunden- oder Business-Profil-Serializer für Listenansichten
class ProfileListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Benutzerinformationen verschachteln

    class Meta:
        model = User
        fields = [
            'user',  # Verschachteltes User-Objekt
            'file', 'location', 'tel', 'description',
            'working_hours', 'type'
        ]

    def get_user(self, obj):
        """
        Erstellt das verschachtelte `user`-Objekt.
        """
        if obj:
            return {
                'pk': obj.pk,
                'username': obj.username or "Unbekannt",
                'first_name': obj.first_name or "",
                'last_name': obj.last_name or ""
            }
        return {
            'pk': None,
            'username': "Unbekannt",
            'first_name': "",
            'last_name': ""
        }


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
