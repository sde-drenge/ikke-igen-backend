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


class TeacherInvite(BaseModel):
    email = models.EmailField()
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="teacherInvites",
    )
    invitedBy = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sentTeacherInvites",
    )
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invite for {self.email} to {self.school.name}"

    def acceptLink(self):
        return f"https://ikkeigen.dk/api/accept-invite/{self.uuid.hex}"
