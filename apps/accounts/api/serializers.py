from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """

    username = serializers.CharField(
        max_length=150,
    )

    password = serializers.CharField(
        write_only=True,
        style={
            "input_type": "password",
        },
    )


class AccountActivationSerializer(serializers.Serializer):
    """
    Serializer for employee account activation.
    """

    token = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        style={
            "input_type": "password",
        },
    )

    def validate_password(self, value):
        """
        Validate the password against Django's
        configured password validators.
        """

        validate_password(
            password=value,
        )

        return value