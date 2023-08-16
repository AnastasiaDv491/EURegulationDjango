"""
    Collection of classes related to entities and securities
"""

from django.db import models


class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating
       created and modified fields.

    Args:
        models (django.db.models.Model): standard django model template
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        app_label = "db"


class Entity(TimeStampedModel):
    """[summary]

    Args:
        TimeStampedModel ([type]): [description]
    """

    name = models.CharField(max_length=128)
    type = models.CharField(max_length=64, null=True)
    country = models.ForeignKey(
        "Country", null=True, on_delete=models.SET("Country deleted")
    )
    industry = models.CharField(max_length=64, null=True)
    sector = models.CharField(max_length=64, null=True)
    factset_entity_id = models.CharField(max_length=16, null=True, unique=True)
    lei_code = models.CharField(max_length=20, null=True)
    institution_id = models.CharField(max_length=16, null=True)
    nace_code = models.CharField(max_length=10, null=True, default=None)

    class Meta:
        unique_together = (("name", "type"),)
        app_label = "db"


class Security(TimeStampedModel):
    """[summary]

    Args:
        TimeStampedModel ([type]): [description]
    """

    isin = models.CharField(max_length=12, null=True, unique=True)  # Unique if exists
    name = models.CharField(max_length=258)
    type = models.CharField(max_length=32)
    exchange = models.CharField(max_length=8, null=True)
    currency = models.CharField(max_length=4, null=True)
    fsym_id = models.CharField(max_length=16)
    primary = models.BooleanField()
    ticker = models.CharField(max_length=64, null=True)
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE)
