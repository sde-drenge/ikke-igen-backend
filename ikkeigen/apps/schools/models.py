from django.db import models
from users.models import BaseModel, User


class School(BaseModel):
    name = models.CharField(max_length=255)
    address = models.TextField()

    students = models.ManyToManyField(
        User,
        related_name="schools",
        blank=True,
    )

    teachers = models.ManyToManyField(
        User,
        related_name="teachingSchools",
        blank=True,
    )

    def __str__(self):
        return self.name
