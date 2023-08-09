from django.db import models
from .utils import TimeStampedModel

class Regulation(TimeStampedModel):
    """ The class representing a piece of regulation

    Args:
        TimeStampedModel (abstract django model): class that provides
            self-updating created and modified fields
    """
    doc_code = models.CharField(max_length=3, primary_key=True)
    title = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256, unique=True)   
    celex_code = models.CharField(max_length=256, unique=True)
    publication_date = models.CharField(max_length=256, unique=True)
    doc_type = models.CharField(max_length=256, unique=True)
    doc_type_code = models.CharField(max_length=256, unique=True)
    author = models.CharField(max_length=256, unique=True)
    languages = models.CharField(max_length=256, unique=True)
    quicksearch_url = models.CharField(max_length=256, unique=True)
    classification = models.CharField(max_length=256, unique=True)
    date_effect = models.CharField(max_length=256, unique=True)
    date_deadline = models.CharField(max_length=256, unique=True)
    date_sig = models.CharField(max_length=256, unique=True)

    class Meta:
        app_label = 'db'


class RegulationRelation(TimeStampedModel):
    """ The class representing a relation between two pieces of regulation

    Args:
        TimeStampedModel (abstract django model): class that provides
            self-updating created and modified fields
    """
    source = models.ForeignKey('Regulation', related_name='sources', on_delete=models.CASCADE)
    target = models.ForeignKey('Regulation', related_name='targets', on_delete=models.CASCADE)
    relation_type = models.CharField(max_length=32)

    class Meta:
        app_label = 'db'
        unique_together = ('source', 'target', 'relation_type')