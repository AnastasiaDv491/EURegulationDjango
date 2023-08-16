from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('list/', views.all_listings, name="product-list")

]