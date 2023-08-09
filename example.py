"""
    Just an example of how to use the RiskConcileData package. We have provided you with
    a modified version of the package that prevents you from accessing or modyfing the
    production database. You are working on our development database. This is a perfect
    copy of the production database and we use it as well whenever we are developing.

    The example will interact with the Entity model using django.
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RiskconcileData.settings')
django.setup()

from RiskconcileData.db.models import Entity


# Getting information on an entity
first_entity = Entity.objects.first()
print('Name: ', first_entity.name)

# Basic filter query
apple = Entity.objects.filter(name='Apple, Inc.').first()
print('Apple\'s Nace code: ', apple.nace_code)

# Creating a new entity
new_entity = Entity(
    name='Fictional Corp.', 
    type='Public Company',
    industry=4810,
    sector=4800,
    factset_entity_id=None,
    lei_code=None,
    institution_id=None,
    country_id='BEL',
    nace_code='64.19'
    )
new_entity.save() # stores it in the databse

check = Entity.objects.filter(name='Fictional Corp.').first()
print('New entity\'s name: ', check.name)

# Updating an entity
check.type = 'Subsidiary'
check.save()

check_2 = Entity.objects.filter(name='Fictional Corp.').first()
print('New entity\'s type: ', check_2.type)

# Removing an entity
check_2.delete()