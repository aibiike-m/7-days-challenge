from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ["email", "password", "re_password"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "display_name", "language"]
        read_only_fields = ["email"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect current password")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        validate_password(attrs["new_password"], self.context["request"].user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        if user.has_usable_password():
            raise serializers.ValidationError(
                "You already have a password set. Use the password change function."
            )

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )

        validate_password(attrs["new_password"], user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RequestEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)

    def validate_new_email(self, value):
        user = self.context["request"].user

        if value == user.email:
            raise serializers.ValidationError("New email matches current email")

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use")

        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ConfirmEmailChangeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DeleteAccountWithPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect password")
        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value.lower()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ConfirmPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        try:
            user = User.objects.get(email=attrs["email"].lower())
            validate_password(attrs["new_password"], user)
        except User.DoesNotExist:
            pass
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
