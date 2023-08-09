""""
    Just an example of how to use the RiskConcileData package. We have provided you with
    a modified version of the package that prevents you from accessing or modyfing the
    production database. You are working on our development database. This is a perfect
    copy of the production database and we use it as well whenever we are developing.

    The example will interact with the Entity model using django.
"""
import django
import os
from django.core.management import BaseCommand
from csv import DictReader
import pandas as pd
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RiskconcileData.settings')
django.setup()

from RiskconcileData.db.models import Entity, Regulation, RegulationRelation


# # Getting information on an entity
# first_entity = Entity.objects.first()
# print('Name: ', first_entity.name)

# # Basic filter query
# apple = Entity.objects.filter(name='Apple, Inc.').first()
# print('Apple\'s Nace code: ', apple.nace_code)

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

# TODO: change the code to populate the new objects only 

def clean_regulation_table(csv_file_regulation):
    df_regulation = pd.read_csv(csv_file_regulation)
    df_regulation["date_sig"] = df_regulation["date_sig"].str.replace("'", "")
    df_regulation["date_effect"] = df_regulation["date_effect"].str.replace("'", "")
    df_regulation["date_deadline"] = df_regulation["date_deadline"].str.replace("'", "")

    df_regulation["date_effect"] = df_regulation["date_effect"].replace("Not found", np.nan)
    df_regulation["date_sig"] = df_regulation["date_sig"].replace("Not found", np.nan)

    df_regulation["date_deadline"] = df_regulation["date_deadline"].replace("Not found", np.nan)
    # print(df_regulation.dtypes)

    df_regulation["publication_date"] = pd.to_datetime(df_regulation["publication_date"], format = "%d/%m/%Y")
    df_regulation["date_effect"] = pd.to_datetime(df_regulation["date_effect"], format = "%d/%m/%Y")
    df_regulation["date_sig"] = pd.to_datetime(df_regulation["date_sig"], format = "%d/%m/%Y")
    df_regulation["date_deadline"] = pd.to_datetime(df_regulation["date_deadline"], format = "%d/%m/%Y")

    df_regulation["publication_date"] = df_regulation["publication_date"].dt.strftime("%Y-%m-%d")
    # df_regulation["publication_date"] = df_regulation["publication_date"].astype("string")

    df_regulation["date_effect"] = df_regulation["date_effect"].dt.strftime("%Y-%m-%d")
    # df_regulation["date_effect"] = df_regulation["date_effect"].astype("string")

    df_regulation["date_sig"] = df_regulation["date_sig"].dt.strftime("%Y-%m-%d")
    # df_regulation["date_sig"] = df_regulation["date_sig"].astype("string")

    df_regulation["date_deadline"] = df_regulation["date_deadline"].dt.strftime("%Y-%m-%d")
    # df_regulation["date_deadline"] = df_regulation["date_deadline"].astype("string")
    
    df_regulation = df_regulation.replace([pd.NaT], [None])
    df_regulation.to_csv("./data/cleaned_primary_secondary_regulations.csv", index = False)
    return df_regulation


# for _, row in clean_regulation_table("./data/primary_secondary_regulations.csv").iterrows():
    
#     regulation=Regulation(doc_code=row['doc_code'], title=row['title'], 
#                         name=row['name'], celex_code = row["celex_code"],
#                         publication_date = row["publication_date"],doc_type = row["doc_type"],doc_type_code = row["doc_type_code"],
#                         author = row["author"], languages = row["languages"],quicksearch_url = row["quicksearch_url"],
#                         date_effect = row["date_effect"], classification = row["classification"],
#                         date_deadline = row["date_deadline"],date_sig = row["date_sig"])  
#     regulation.save()


# Either doc_code to give OR source__doc_code = row[source]
df_regulations = clean_regulation_table("./data/primary_secondary_regulations.csv")
df_relations = pd.read_csv("./data/full_df.csv")
df_relations = df_relations.drop_duplicates()

for _, row in df_relations.iterrows():
    for i in range(len(df_regulations)):
        if row.source in df_regulations.loc[i, "doc_code"] and row.target in df_regulations.loc[i, "doc_code"]:
            print(row.source, row.target)
    # regulation=Regulation(source__doc_code =row['source'], target__doc_code=row['target'], 
    #                     name=row['name'])  
    # regulation.save()