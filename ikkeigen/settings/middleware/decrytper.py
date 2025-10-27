import base64
import json
from datetime import datetime, timedelta

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.views import APIView

BLOCK_SIZE = 128


def getSecret():
    return settings.DEFAULTSETTINGS.get("PRIVATE_KEY")


def getPublicKey():
    return settings.DEFAULTSETTINGS.get("PUBLIC_KEY")


def encrypt_data(data):
    if not isinstance(data, bytes):
        data = str(data)
        data = data.replace("'", '"')
        data = data.encode("utf-8")
    publicKey = getPublicKey()

    encryptedData = publicKey.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(encryptedData).decode("utf-8")


def decrypt_data(encryptedData):
    privateKey = getSecret()
    # Decode the base64 data back to binary format
    encryptedData = base64.b64decode(encryptedData)

    # Decrypt the data
    decryptedData = privateKey.decrypt(
        encryptedData,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return decryptedData.decode("utf-8")  # Convert bytes to string if needed


class RequestTimeLoggingMiddleware(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if not hasattr(request, "data"):
            return self.get_response(request)

        data = request.data
        encryptedFields = data.get("encryptedFields")
        if encryptedFields and len(encryptedFields) > 0:
            try:
                fields = decrypt_data(encryptedFields)
                try:
                    fields = json.loads(fields)
                except:
                    pass

                encryptedDate = fields.get("encryptedDate")
                if not encryptedDate:
                    return

                today = datetime.now()
                encryptedDate = datetime.fromisoformat(encryptedDate).replace(
                    tzinfo=None
                )
                if encryptedDate < today - timedelta(seconds=30):
                    return

                for encryptedField in fields:
                    request.data[encryptedField] = fields[encryptedField]

            except Exception as e:
                from .error_handling import sendDiscordMessage

                sendDiscordMessage(str(e))

                raise serializers.ValidationError(
                    "De enrypteret data er ugyldig eller udløbet."
                )
