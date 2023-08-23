from django.shortcuts import render
import pandas as pd
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "RiskconcileData.settings")
django.setup()

from RiskconcileData.db.models import Regulation, RegulationRelation
from .filters import RegFilter

# function to merge both databases
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
  """
  Object that carries information about sources and targets in a graph like form
  """
  def __init__(self, doc_code, target_rel=[], rel_type="", url="", doc_type=""):
    self.doc_code = doc_code
    self.target_rel = target_rel
    self.rel_type = rel_type
    self.url = url
    self.doc_type = doc_type


j = 0
depth = 500
# regulationsFetched = []
def get_target(node, merged_table2,regulationsFetched):
    """
    A recursive function to retrieve sources and their targets
    Input: node object & merged table
    
    """
    global j

    if j <= depth:
        table = merged_table2[merged_table2["source_id"]==node.doc_code]

        for target, rel, url, doc_type in list(zip(table["target_id"], table["relation_type"], table["quicksearch_url_y"], table["name_trg"])):                              
            node.target_rel.append(Node(doc_code=target,target_rel=[], rel_type=rel, url=url, doc_type=doc_type))
            j += 1
        for i in node.target_rel:
            if i.doc_code not in regulationsFetched:

                regulationsFetched.append(i.doc_code) 
                get_target(i, merged_table2,regulationsFetched)
    
def all_listings(request):
    """
    Function that processes doc code filter results
    output: filtered table "Regulation"
    """
    all_listings = Regulation.objects.using('riskconcilemodels').order_by('publication_date')
    my_Filter = RegFilter(request.GET, queryset=all_listings) 
    all_listings = my_Filter.qs
    context = {"all_listings": all_listings, "my_Filter": my_Filter}

    return render(request, 'EURegulationApp/regulation_details.html', {"context":context})

def get_rel(doc_code):
    """
    Function that returns all node objects based on a given doc code
    Input: doc code
    Output: node object 
    """

    df_regulation = pd.DataFrame(Regulation.objects.using('riskconcilemodels').all().values())
    df_relation = pd.DataFrame(RegulationRelation.objects.using('riskconcilemodels').all().values())
    merged_table = merge_Reg_Rel_tables(df_regulation,df_relation)
    merged_table = merged_table.sort_values(by=['date_effect_y'])
    node_obj = Node(doc_code=doc_code,target_rel=[])
    regulationsFetched = []
    get_target(node_obj, merged_table,regulationsFetched)

    return node_obj


def regulation(request, doc_code):
    """
    Function that filters "Regulation" table based on the doc code that is passed on "regulation_details.html" page
    input: doc code
    Ouptut: detailed information about a given regulation
    """
    posts = Regulation.objects.using('riskconcilemodels').filter(doc_code = doc_code)
    
    j = 0
    node_retrieved = get_rel(doc_code)
    
    return render(request, 'EURegulationApp/regulation.html', {'regulation': posts,"doc":doc_code,"node":node_retrieved, "target_rel": node_retrieved.target_rel})




