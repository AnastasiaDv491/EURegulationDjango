from django.urls import path,re_path
from . import views

urlpatterns = [
    path('', views.all_listings, name="product-list"),
    # path('regulation_relationships/', views.get_relations, name="rel_list"),

    re_path(r'^regulation/(?P<doc_code>[^/]+/[0-9]+)', views.regulation, name='regulation'),
]