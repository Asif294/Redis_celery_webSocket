from django.contrib import admin
from django.urls import path,include
from .views import ProductListView,SendMailAPIView
from .import views
urlpatterns = [
   path('products/', ProductListView.as_view(), name='product-list'),
   path('send-mail/', SendMailAPIView.as_view(), name='send-mail'),
   
]