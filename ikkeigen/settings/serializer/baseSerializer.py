from django.conf import settings
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Is used to handle image Url's. We want to remove the standard url, and only store the path in the database
    """

    @property
    def firebaseUrl(self):
        return str(settings.DEFAULTSETTINGS.get("FIREBASE_IMAGE_URL"))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in data.keys():
            dataField = data[field]
            if (
                isinstance(dataField, str)
                and dataField.startswith("/o/")
                and field.lower().endswith("url")
            ):
                data[field] = self.firebaseUrl + dataField
        return data

    def to_internal_value(self, data):
        returnValue = super().to_internal_value(data)
        for field in returnValue.keys():
            dataField = returnValue[field]
            if isinstance(dataField, str) and dataField.startswith(self.firebaseUrl):
                returnValue[field] = dataField.replace(self.firebaseUrl, "")
        return returnValue
