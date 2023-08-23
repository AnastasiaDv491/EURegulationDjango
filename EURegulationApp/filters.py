import django_filters
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RiskconcileData.settings")
django.setup()

from RiskconcileData.db.models import Regulation

class RegFilter(django_filters.FilterSet):
        
    doc_code = django_filters.CharFilter(label='Document code', lookup_expr='icontains',)
    publication_date = django_filters.CharFilter(label='Publication date (YYYY-MM-DD)', lookup_expr='icontains')
    name = django_filters.CharFilter(label='Document name',lookup_expr='icontains')

    class Meta:
        model = Regulation
        fields = ["doc_code", "publication_date", "name"]

