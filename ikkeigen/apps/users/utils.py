import random

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from schools.models import TeacherInvite

from users.models import User


def generateVerificationId(length=6):
    characters = "abcdefghijklmnopqrstuvxyz".upper()
    numbers = "1234567890"

    verificationCode = ""
    for i in range(0, length):
        if random.randint(0, 1) == 1:  # Choose from numbers
            verificationCode += numbers[random.randint(0, len(numbers) - 1)]
        else:
            verificationCode += characters[random.randint(0, len(characters) - 1)]
    return verificationCode


def sendVerificationEmail(user: User):
    try:
        verificationCode = user.verificationCode
        subject = "Verificer din e-mailadresse"
        body = render_to_string(
            "email/email-verification-da.html",
            {
                "user": user,
                "verificationCode": verificationCode,
            },
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=body,
        )
    except Exception as e:
        print(f"Error sending verification email to {user.email}: {e}")


def sendSchoolInviteEmail(schoolInvite: TeacherInvite):
    try:
        subject = f"Du er blevet inviteret til at deltage i {schoolInvite.school.name} på IkkeIgen"
        body = render_to_string(
            "email/school-invite-da.html",
            {
                "invitationLink": f"https://ikkeigen.dk/api/accept-invite/{schoolInvite.uuid.hex}",
                "schoolName": schoolInvite.school.name,
                "inviteeName": schoolInvite.invitedBy.getFullName(),
            },
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[schoolInvite.email],
            html_message=body,
        )
    except Exception as e:
        print(f"Error sending school invite email to {schoolInvite.email}: {e}")
