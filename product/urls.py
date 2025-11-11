from django.contrib import admin
from django.urls import path,include
from .views import ProductListView
from .import views
urlpatterns = [
   path('products/', ProductListView.as_view(), name='product-list'),
   path('home/',views.index,name='home')
]