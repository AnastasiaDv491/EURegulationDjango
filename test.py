from django.shortcuts import render
from django_filters.views import FilterView

import pandas as pd
import numpy as np
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RiskconcileData.settings")
django.setup()

from RiskconcileData.db.models import Regulation, RegulationRelation

def merge_Reg_Rel_tables(reg_table, rel_table):

    reg_table = reg_table.rename(columns={"doc_code": "source_id"})
    # Merge using "source" column
    merged_table =pd.merge(rel_table,reg_table, on = "source_id", how = 'left')
    merged_table=merged_table.rename(columns={"name": "name_src", "celex_code": "celex_code_src","title": "title_src", "publication_date": "publication_date_src", "doc_type":"doc_type_src","doc_type_code": "doc_type_src", "author": "author_src", "languages":"languages_src", "url": "url_src"})

    # Merge using "target" column
    reg_table = reg_table.rename(columns={"source_id": "target_id"})
    merged_table = merged_table.merge(reg_table, how = 'left', on = "target_id")
    merged_table=merged_table.rename(columns={"name": "name_trg", "celex_code": "celex_code_trg","title": "title_trg", "publication_date": "publication_date_trg", "doc_type":"doc_type_trg","doc_type_code": "doc_type_trg", "author": "author_trg", "languages":"languages_trg", "url": "url_trg"})
    merged_table = merged_table.fillna(value = "Not found")
    merged_table = merged_table.drop_duplicates()

    return merged_table

source = "2019/1156"
df_regulation = pd.DataFrame(Regulation.objects.all().values())
df_relation = pd.DataFrame(RegulationRelation.objects.all().values())
merged_table2 = merge_Reg_Rel_tables(df_regulation,df_relation)

class Node:
  def __init__(self, doc_code, target_rel=[]):
    self.doc_code = doc_code
    self.target_rel = target_rel


j = 0
depth = 500

def get_target(node, merged_table2):
    global j

    if j < depth:
        print(node.doc_code)
        merged_table2 = merged_table2[merged_table2["source_id"]==node.doc_code]
        for target, rel in zip(merged_table2["target_id"], merged_table2["relation_type"]):
            print(target, rel)
            node.target_rel.append([Node(doc_code=target), rel])
        j += 1

        for i in node.target_rel:
            get_target(i[0], merged_table2)


node = Node(doc_code="2019/1156")
get_target(node, merged_table2)
# print(node.target_rel[0][0].target_rel)

# for i in node.target_rel:
#    print(i[0].doc_code)
#    for j in i[0].target_rel:
#       print("--"+j[0].doc_code)