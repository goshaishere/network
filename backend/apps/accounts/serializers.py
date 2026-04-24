from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .exceptions import CaptchaRequired
from .services.captcha import verify_hcaptcha_response
from .services.login_attempts import clear_fail, fail_key, get_fail_count, increment_fail

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "display_name", "is_staff")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "display_name", "password", "password_confirm")

    def validate_email(self, value: str) -> str:
        return value.strip().lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": ["Пароли не совпадают."]})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        display_name = (validated_data.pop("display_name", None) or "").strip()
        user = User(email=email, display_name=display_name, is_active=True)
        user.set_password(password)
        user.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Принимает поле `email` вместо `username`; опционально `captcha_token` после N ошибок."""

    username_field = User.USERNAME_FIELD
    captcha_token = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()

    def validate(self, attrs):
        request = self.context.get("request")
        email = (attrs.get(self.username_field) or "").strip().lower()
        key = fail_key(request, email) if request else ""
        fails = get_fail_count(key) if key else 0
        threshold = getattr(settings, "LOGIN_CAPTCHA_THRESHOLD", 3)
        raw_captcha = (self.initial_data or {}).get("captcha_token")
        if fails >= threshold:
            if not verify_hcaptcha_response(raw_captcha if isinstance(raw_captcha, str) else None):
                raise CaptchaRequired()
        try:
            data = super().validate(attrs)
        except (serializers.ValidationError, AuthenticationFailed):
            if key:
                increment_fail(key)
            raise
        if key:
            clear_fail(key)
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": ["Пароли не совпадают."]}
            )
        validate_password(attrs["new_password"])
        return attrs
