from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from .models import Review

User = get_user_model()


class UserNestedSerializer(serializers.ModelSerializer):
    """
    Nested serializer for user details.
    - Used in list views of customer or business profiles.
    - Displays basic information such as ID, username, first name, and last name.
    """

    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name']


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    - Creates a new user based on the provided data.
    - Validates the input data and saves the user.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'type']  

    def create(self, validated_data):
        """
        Creates a new user with the validated data.
        - Ensures the password is securely stored.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email'),
            type=validated_data.get('type', 'customer')  # Default type is 'customer'
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    - Validates login credentials (username and password).
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the login credentials.
        - Checks if the username and password are correct.
        """
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    return user
                else:
                    raise serializers.ValidationError("User account is deactivated.")
            else:
                raise serializers.ValidationError("Invalid login credentials.")
        else:
            raise serializers.ValidationError("Both fields must be filled out.")


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user management.
    - Used to display and update user details.
    """
    user = serializers.IntegerField(source='id', read_only=True) 

    class Meta:
        model = User
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location',
            'tel', 'description', 'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['pk', 'username', 'created_at']
        extra_kwargs = {
            'first_name': {'required': False, 'allow_null': True, 'default': 'Unknown'},
            'last_name': {'required': False, 'allow_null': True, 'default': 'Unknown'},
            'file': {'required': False, 'allow_null': True, 'default': 'no_file'},
            'location': {'required': False, 'allow_null': True, 'default': 'no_address'},
            'tel': {'required': False, 'allow_null': True, 'default': 'no_phone_number'},
            'description': {'required': False, 'allow_null': True, 'default': 'no_description'},
            'working_hours': {'required': False, 'allow_null': True, 'default': 'no_working_hours'},
        }


class ProfileListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing user profiles.
    - Used to display basic information about users.
    - Includes nested user information.
    """
    user = serializers.SerializerMethodField()  

    class Meta:
        model = User
        fields = [
            'user',  
            'file', 'location', 'tel', 'description',
            'working_hours', 'type'
        ]

    def get_user(self, obj):
        """
        Returns nested user information.
        - Includes ID, username, first name, and last name.
        """
        return {
            'pk': getattr(obj, 'pk', None),
            'username': getattr(obj, 'username', "Unknown") or "Unknown",
            'first_name': getattr(obj, 'first_name', "Unknown") or "Unknown",
            'last_name': getattr(obj, 'last_name', "Unknown") or "Unknown"
        }

    def to_representation(self, instance):
        """
        Overrides the default representation of a profile.
        - Sets default values for fields that are null.
        """
        representation = super().to_representation(instance)

        representation['file'] = representation.get('file') if representation.get('file') is not None else 'no_file'
        representation['location'] = representation.get('location') if representation.get('location') is not None else 'no_address'
        representation['tel'] = representation.get('tel') if representation.get('tel') is not None else 'no_phone_number'
        representation['description'] = representation.get('description') if representation.get('description') is not None else 'no_description'
        representation['working_hours'] = representation.get('working_hours') if representation.get('working_hours') is not None else 'no_working_hours'

        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for managing reviews.
    - Supports creating and displaying reviews.
    """
    class Meta:
        model = Review
        fields = '__all__'
