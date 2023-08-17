from django.shortcuts import render
from django_filters.views import FilterView
from collections import OrderedDict

import pandas as pd
import numpy as np
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RiskconcileData.settings")
django.setup()

from RiskconcileData.db.models import Regulation, RegulationRelation
from .filters import RegFilter

# Create your views here.
def main_page(request):
    regulations = list(Regulation.objects.using('riskconcilemodels').values_list("doc_code", flat = True).distinct())
    return render(request, 'EURegulationApp/main_page.html', {'regulations':regulations})


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


class Node:
  def __init__(self, doc_code, target_rel=[]):
    self.doc_code = doc_code
    self.target_rel = target_rel


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

        for target, rel in zip(test["target_id"], test["relation_type"]):
            # print(target, rel)
               
            node.target_rel.append([Node(doc_code=target,target_rel=[]),rel])
            j += 1

        print("")
        for i in node.target_rel:
            if i[0].doc_code not in regulationsFetched:
                # print("loop2 " +i[0].doc_code)

                regulationsFetched.append(i[0].doc_code) 
                get_target(i[0], merged_table2)



# node = Node(doc_code="2019/1156")

def all_listings(request):
    all_listings = Regulation.objects.using('riskconcilemodels').order_by('publication_date')
    my_Filter = RegFilter(request.GET, queryset=all_listings) 
    all_listings = my_Filter.qs
    context = {"all_listings": all_listings, "my_Filter": my_Filter}
    if len(all_listings) > 0:
        df_regulation = pd.DataFrame(Regulation.objects.using('riskconcilemodels').all().values())
        df_relation = pd.DataFrame(RegulationRelation.objects.using('riskconcilemodels').all().values())
        
        # TODO:
        # - add links to sources and targets
        # - add a different view if they search by the date

        for match in all_listings: # can only be one match 
            merged_table = merge_Reg_Rel_tables(df_regulation,df_relation)
            node = Node(doc_code=match.doc_code)
            get_target(node, merged_table)  # return a dict with source codes as keys and other attributes as their values

            merged_table = merged_table[merged_table["source_id"]==match.doc_code]
            if merged_table.empty:
                source_id = ""
                target_ids = ""
                relations = ""
                target_rel = ""
            else:
                source_id = "" # source is always the first key

                other_sources = "" # other regulations that are also sources

                # In HTML: logic that if a value is a source, then it becomes a source
                target_ids = merged_table["target_id"].values.tolist()
                relations = merged_table["relation_type"].values.tolist()
                print(other_sources)
                target_rel = zip(target_ids, relations)
                # merged_table = merged_table[["source_id", "target_id", "relation_type"]]
    
    return render(request, 'EURegulationApp/regulation_details.html', {"context":context,"source": source_id,"other_sources":other_sources, "target_rel": node.target_rel, "node": node})









