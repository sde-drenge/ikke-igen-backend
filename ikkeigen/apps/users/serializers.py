from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True, format="hex")
    createdAt = serializers.DateTimeField(read_only=True)
    isActive = serializers.BooleanField(read_only=True)
    phoneNumber = serializers.CharField(
        allow_blank=True, required=False, allow_null=True
    )
    profileColor = serializers.CharField(
        read_only=True,
    )
    schoolName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "uuid",
            "email",
            "phoneNumber",
            "firstName",
            "lastName",
            "education",
            "schoolName",
            "role",
            "profileColor",
            "isActive",
            "createdAt",
        )

    def get_user(self, email, exclude=None):
        user = None
        user = User.objects.filter(email__iexact=email, deletedAt__isnull=True)
        if exclude:
            user.exclude(uuid=exclude)
        user = user.first()
        return user

    def validate_email(self, value):
        user = self.instance

        if value == user.email:
            return user.email

        # Ensure the user doesn't already exist
        email = value.lower()
        user: User | None = self.get_user(email, user.uuid)
        if user:
            raise serializers.ValidationError(
                "En bruger med denne e-mail findes allerede. Prøv at logge ind."
            )

        return email

    def get_schoolName(self, obj: User) -> str | None:
        school = obj.schools.first()
        if not school:
            return None

        return school.name


class LightUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "firstName",
            "lastName",
            "email",
            "role",
            "education",
            "profileColor",
        )


class UserCreatorSerializer(UserSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ("email",)

    def validate_email(self, value):
        # Ensure the user doesn't already exist
        email = value.lower()
        user: User | None = self.get_user(email)
        if user:
            raise serializers.ValidationError(
                _("A user with this e-mail already exists. Try to login.")
            )

        return email
