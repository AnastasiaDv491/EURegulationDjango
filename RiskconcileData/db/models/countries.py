"""
    Collection of classes related to countries
"""

from django.db import models
from .utils import TimeStampedModel


class Country(TimeStampedModel):
    """ The class representing a country

    Args:
        TimeStampedModel (abstract django model): class that provides
            self-updating created and modified fields
    """

    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    region = models.CharField(max_length=32, null=True)
    currency = models.CharField(max_length=3, null=True)

    class Meta:
        verbose_name_plural = "Countries"
        app_label = "db"
