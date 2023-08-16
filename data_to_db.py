""""
    Just an example of how to use the RiskConcileData package. We have provided you with
    a modified version of the package that prevents you from accessing or modyfing the
    production database. You are working on our development database. This is a perfect
    copy of the production database and we use it as well whenever we are developing.

    The example will interact with the Entity model using django.
"""
import django
import os
import pandas as pd
import numpy as np

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RiskconcileData.settings")
django.setup()

from RiskconcileData.db.models import Entity, Regulation, RegulationRelation


# # Getting information on an entity
first_entity = Entity.objects.all()
print(first_entity.doc_code)




# TODO: change the code to populate the new objects only


def clean_regulation_table(csv_file_regulation):
    df_regulation = pd.read_csv(csv_file_regulation)
    df_regulation["date_sig"] = df_regulation["date_sig"].str.replace("'", "")
    df_regulation["date_effect"] = df_regulation["date_effect"].str.replace("'", "")
    df_regulation["date_deadline"] = df_regulation["date_deadline"].str.replace("'", "")

    df_regulation["date_effect"] = df_regulation["date_effect"].replace(
        "Not found", np.nan
    )
    df_regulation["date_sig"] = df_regulation["date_sig"].replace("Not found", np.nan)
    df_regulation["date_deadline"] = df_regulation["date_deadline"].replace(
        "Not found", np.nan
    )

    df_regulation["publication_date"] = pd.to_datetime(
        df_regulation["publication_date"], format="%d/%m/%Y"
    )
    df_regulation["date_effect"] = pd.to_datetime(
        df_regulation["date_effect"], format="%d/%m/%Y"
    )
    df_regulation["date_sig"] = pd.to_datetime(
        df_regulation["date_sig"], format="%d/%m/%Y"
    )
    df_regulation["date_deadline"] = pd.to_datetime(
        df_regulation["date_deadline"], format="%d/%m/%Y"
    )

    df_regulation["publication_date"] = df_regulation["publication_date"].dt.strftime(
        "%Y-%m-%d"
    )
    df_regulation["date_effect"] = df_regulation["date_effect"].dt.strftime("%Y-%m-%d")
    df_regulation["date_sig"] = df_regulation["date_sig"].dt.strftime("%Y-%m-%d")
    df_regulation["date_deadline"] = df_regulation["date_deadline"].dt.strftime(
        "%Y-%m-%d"
    )

    df_regulation = df_regulation.replace([pd.NaT], [None])
    df_regulation.to_csv(
        "./data/cleaned_primary_secondary_regulations.csv", index=False
    )
    return df_regulation


for _, row in clean_regulation_table("./data/primary_secondary_regulations.csv").iterrows():

    regulation=Regulation(doc_code=row['doc_code'], title=row['title'],
                        name=row['name'], celex_code = row["celex_code"],
                        publication_date = row["publication_date"],doc_type = row["doc_type"],doc_type_code = row["doc_type_code"],
                        author = row["author"], languages = row["languages"],quicksearch_url = row["quicksearch_url"],
                        date_effect = row["date_effect"], classification = row["classification"],
                        date_deadline = row["date_deadline"],date_sig = row["date_sig"])
    regulation.save()


obj = RegulationRelation.objects.all()
obj.delete()

df_regulations = clean_regulation_table("./data/primary_secondary_regulations.csv")
df_relations = pd.read_csv("./data/full_df.csv")
df_relations = df_relations.drop_duplicates()


def merge_datframes(regulation, relation):
    regulation = regulation.drop("Unnamed: 0", axis=1)
    regulation = regulation.rename(columns={"doc_code": "source"})
    df1 = relation[["source", "target", "relation"]].merge(
        regulation[["source"]], on="source", how="inner"
    )

    regulation = regulation.rename(columns={"source": "target"})
    final_df = df1[["source", "target", "relation"]].merge(
        regulation[["target"]], on="target", how="inner"
    )
    final_df["relation"] = final_df["relation"].astype("string")
    final_df["source"] = final_df["source"].astype("string")
    final_df["target"] = final_df["target"].astype("string")

    return final_df


final_df = merge_datframes(df_regulations, df_relations)

for _, row in final_df.iterrows():
    source_object = Regulation.objects.get(doc_code=row["source"])
    target_object = Regulation.objects.get(doc_code=row["target"])
    relation = row["relation"]

    usershipping, created = RegulationRelation.objects.get_or_create(
        source=source_object, target=target_object, relation_type=relation
    )
    usershipping.save()
