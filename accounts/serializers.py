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
            'first_name': {'required': False, 'allow_null': True, 'default': 'Unbekannt'},
            'last_name': {'required': False, 'allow_null': True, 'default': 'Unbekannt'},
            'file': {'required': False, 'allow_null': True, 'default': 'keine_datei'},  # Beispiel für Standardwert
            'location': {'required': False, 'allow_null': True, 'default': 'keine_Adresse'},  # Beispiel für Standardwert
            'tel': {'required': False, 'allow_null': True, 'default': 'keine_Telefonnummer'},  # Beispiel für Standardwert
            'description': {'required': False, 'allow_null': True, 'default': 'keine_Beschreibung'},  # Beispiel für Standardwert
            'working_hours': {'required': False, 'allow_null': True, 'default': 'keine_Arbeitszeiten'},  # Beispiel für Standardwert
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
        return {
            'pk': getattr(obj, 'pk', None),
            'username': getattr(obj, 'username', "Unbekannt") or "Unbekannt",
            'first_name': getattr(obj, 'first_name', "Unbekannt") or "Unbekannt",
            'last_name': getattr(obj, 'last_name', "Unbekannt") or "Unbekannt"
        }

    def to_representation(self, instance):
        # Standardwerte setzen, falls Felder null sind
        representation = super().to_representation(instance)
        
        # Überprüfen und Standardwerte setzen, falls null
        representation['file'] = representation.get('file') if representation.get('file') is not None else 'keine_datei'
        representation['location'] = representation.get('location') if representation.get('location') is not None else 'keine_Adresse'
        representation['tel'] = representation.get('tel') if representation.get('tel') is not None else 'keine_Telefonnummer'
        representation['description'] = representation.get('description') if representation.get('description') is not None else 'keine_Beschreibung'
        representation['working_hours'] = representation.get('working_hours') if representation.get('working_hours') is not None else 'keine_Arbeitszeiten'
        
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
