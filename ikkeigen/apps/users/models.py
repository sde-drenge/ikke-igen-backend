import random
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext as _


class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    updatedAt = models.DateTimeField(blank=True, null=True, auto_now=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    deletedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        # This makes the model abstract, so it won’t create a database table
        abstract = True


def randomColor():
    colors = [
        "#87CEEB",
        "#40E0D0",
        "#3399dc",
        "#5edc5e",
        "#f0c040",
        "#FFD24D",
        "#66c255",
        "#ff8a66",
        "#ca8de6",
        "#f255aa",
        "#cdf28c",
    ]
    random.shuffle(colors)
    return colors[0]


class User(AbstractUser, BaseModel):
    username = None
    email = models.EmailField(unique=True)
    phoneNumber = models.CharField(max_length=15, null=True, blank=True)
    firstName = models.CharField(max_length=64, blank=True)
    lastName = models.CharField(max_length=64, blank=True)

    education = models.CharField(
        max_length=128,
        blank=True,
        null=True,
    )

    isActive = models.BooleanField(default=False)

    verificationEmailSentAt = models.DateTimeField(blank=True, null=True)
    verificationCode = models.CharField(max_length=6, null=True, blank=True)

    profileColor = models.CharField(
        max_length=32, null=False, blank=False, default=randomColor
    )

    role = models.CharField(
        max_length=16,
        choices=[
            ("student", "Student"),
            ("teacher", "Teacher"),
            ("teacher-admin", "Teacher Admin"),
            ("admin", "Admin"),
        ],
        default="student",
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return "[{pk}] {email}".format(pk=self.pk, email=self.email)

    def getFullName(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.firstName, self.lastName)
        return full_name.strip()

    @property
    def is_authenticated(self):
        if self.pk is None or not self.isActive:
            return False
        return True

    def updateLastLogin(self):
        """
        A signal receiver which updates the last_login date for
        the user logging in.
        """
        self.last_login = timezone.now()
        self.save(update_fields=["last_login"])


def createSuperuser(email, password):
    user = User.objects.create(
        email=email,
        is_staff=True,
        isActive=True,
        is_superuser=True,
    )
    user.set_password(password)
    user.save()
    return user
