from django.db import models
from .utils import TimeStampedModel


class Regulation(TimeStampedModel):
    """ The class representing a piece of regulation

    Args:
        TimeStampedModel (abstract django model): class that provides
            self-updating created and modified fields
    """

    doc_code = models.CharField(max_length=32, primary_key=True)
    title = models.TextField(unique=True, default="")
    name = models.CharField(max_length=256, null=True)
    celex_code = models.CharField(max_length=64, unique=True, default="")
    publication_date = models.DateField(default="1999-12-31")
    doc_type = models.CharField(max_length=64, null=True)
    doc_type_code = models.CharField(max_length=64, null=True)
    author = models.TextField(null=True)
    languages = models.TextField(null=True)
    quicksearch_url = models.TextField(null=True)
    classification = models.TextField(null=True)
    date_effect = models.DateField(null=True)
    date_deadline = models.DateField(null=True)
    date_sig = models.DateField(null=True)

    class Meta:
        app_label = "db"


class RegulationRelation(TimeStampedModel):
    """ The class representing a relation between two pieces of regulation

    Args:
        TimeStampedModel (abstract django model): class that provides
            self-updating created and modified fields
    """

    source = models.ForeignKey(
        "Regulation", related_name="sources", on_delete=models.CASCADE
    )
    target = models.ForeignKey(
        "Regulation", related_name="targets", on_delete=models.CASCADE
    )
    relation_type = models.CharField(max_length=32)

    class Meta:
        app_label = "db"
        unique_together = ("source", "target", "relation_type")
