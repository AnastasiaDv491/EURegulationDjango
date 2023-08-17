import django_filters
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RiskconcileData.settings")
django.setup()

from RiskconcileData.db.models import Regulation, RegulationRelation

class RegFilter(django_filters.FilterSet):

    class Meta:
        model = Regulation
        fields = ['doc_code', 'publication_date']