from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import Review

User = get_user_model()


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Verschachtelter Serializer für Benutzer.
    - Wird in Listenansichten von Kunden- oder Business-Profilen verwendet.
    - Zeigt grundlegende Informationen wie ID, Benutzername, Vor- und Nachname an.
    """

    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name']


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer für die Benutzerregistrierung.
    - Erstellt einen neuen Benutzer basierend auf den übermittelten Daten.
    - Validiert die Eingabedaten und speichert den Benutzer.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'type']  # Passe die Felder an dein Modell an

    def create(self, validated_data):
        """
        Erstellt einen neuen Benutzer mit den validierten Daten.
        - Das Passwort wird sicher gespeichert.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            type=validated_data.get('type', 'customer')  # Standardwert 'customer'
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer für die Benutzeranmeldung.
    - Validiert die Anmeldedaten (Benutzername und Passwort).
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validiert die Anmeldedaten.
        - Überprüft, ob der Benutzername und das Passwort korrekt sind.
        """
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
    """
    Serializer für die Benutzerverwaltung.
    - Wird verwendet, um Benutzerdetails anzuzeigen und zu aktualisieren.
    """
    user = serializers.IntegerField(source='id', read_only=True)  # Alias für `id`

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['pk', 'username', 'email', 'created_at']
        extra_kwargs = {
            'first_name': {'required': False, 'allow_null': True, 'default': 'Unbekannt'},
            'last_name': {'required': False, 'allow_null': True, 'default': 'Unbekannt'},
            'file': {'required': False, 'allow_null': True, 'default': 'keine_datei'},
            'location': {'required': False, 'allow_null': True, 'default': 'keine_Adresse'},
            'tel': {'required': False, 'allow_null': True, 'default': 'keine_Telefonnummer'},
            'description': {'required': False, 'allow_null': True, 'default': 'keine_Beschreibung'},
            'working_hours': {'required': False, 'allow_null': True, 'default': 'keine_Arbeitszeiten'},
        }


class ProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer für die Liste von Benutzerprofilen.
    - Wird verwendet, um grundlegende Informationen über Benutzer anzuzeigen.
    - Enthält verschachtelte Benutzerinformationen.
    """
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
        Gibt die verschachtelten Benutzerinformationen zurück.
        - Enthält ID, Benutzername, Vor- und Nachname.
        """
        return {
            'pk': getattr(obj, 'pk', None),
            'username': getattr(obj, 'username', "Unbekannt") or "Unbekannt",
            'first_name': getattr(obj, 'first_name', "Unbekannt") or "Unbekannt",
            'last_name': getattr(obj, 'last_name', "Unbekannt") or "Unbekannt"
        }

    def to_representation(self, instance):
        """
        Überschreibt die Standard-Darstellung eines Profils.
        - Setzt Standardwerte für Felder, die null sind.
        """
        representation = super().to_representation(instance)

        # Überprüfen und Standardwerte setzen, falls null
        representation['file'] = representation.get('file') if representation.get('file') is not None else 'keine_datei'
        representation['location'] = representation.get('location') if representation.get('location') is not None else 'keine_Adresse'
        representation['tel'] = representation.get('tel') if representation.get('tel') is not None else 'keine_Telefonnummer'
        representation['description'] = representation.get('description') if representation.get('description') is not None else 'keine_Beschreibung'
        representation['working_hours'] = representation.get('working_hours') if representation.get('working_hours') is not None else 'keine_Arbeitszeiten'

        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer für die Verwaltung von Bewertungen (Reviews).
    - Unterstützt die Erstellung und Anzeige von Bewertungen.
    """
    class Meta:
        model = Review
        fields = '__all__'
