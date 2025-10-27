from django.db import models
from users.models import BaseModel


class Workplace(BaseModel):
    name = models.CharField(max_length=255)
    vat = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.vat}"
