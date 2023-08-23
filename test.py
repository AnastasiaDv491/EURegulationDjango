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
  def __init__(self, doc_code, target_rel=[], rel_type="", url=""):
    self.doc_code = doc_code
    self.target_rel = target_rel
    self.rel_type = rel_type
    self.url = url


j = 0
depth = 500
regulationsFetched = []
def get_target(node, merged_table2):
    global j

    if j <= depth:
        # print(node.doc_code)
        test = merged_table2[merged_table2["source_id"]==node.doc_code]
        # print("doc"+node.doc_code)
        # print(test["target_id"])

        for target, rel, url in list(zip(test["target_id"], test["relation_type"], test["quicksearch_url_y"])):
            # print(target, rel)
               
            node.target_rel.append([Node(doc_code=target,target_rel=[], rel_type=rel, url=url)])
            j += 1

        print("")
        for i in node.target_rel:
            if i[0].doc_code not in regulationsFetched:
          
                regulationsFetched.append(i[0].doc_code) 
                get_target(i[0], merged_table2)
            

def get_rel1(doc_code):
    df_regulation = pd.DataFrame(Regulation.objects.all().values())
    df_relation = pd.DataFrame(RegulationRelation.objects.all().values())
    merged_table = merge_Reg_Rel_tables(df_regulation,df_relation)
    merged_table = merged_table.sort_values(by=['date_effect_y'])
    node_obj = Node(doc_code=doc_code)
    get_target(node_obj, merged_table)
    return node_obj


def regulation(doc_code):
    """
    Function that filters "Regulation" table based on the doc code that is passed on "regulation_details.html" page
    input: doc code
    Ouptut: detailed information about a given regulation
    """
    posts = Regulation.objects.filter(doc_code = doc_code)
    node_retrieved = get_rel1(doc_code)
    return node_retrieved

test = regulation(source)
# print(test.target_rel)

# node = Node(doc_code="2019/1156", target_rel=[])
# get_target(node, merged_table2)

# print("runs",j)
# print("here")
for i in test.target_rel:
   print(i[0].doc_code + " "+i[0].rel_type)

   for j in i[0].target_rel:
      print("--"+j[0].doc_code +" "+j[0].rel_type)      
      for k in j[0].target_rel:
        print("----"+k[0].doc_code +k[0].rel_type)
        for a in k[0].target_rel:
            print("----"+k[0].doc_code +k[0].rel_type)