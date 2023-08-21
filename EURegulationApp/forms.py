from django import forms
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RiskconcileData.settings")
django.setup()

from RiskconcileData.db.models import Regulation, RegulationRelation

class RegForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Regulation
        fields = ["doc_code"]