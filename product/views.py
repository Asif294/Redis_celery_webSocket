from django.shortcuts import render
from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from .models import Products

class ProductListView(APIView):
    def get(self,request):
        product=cache.get('all_products')
        if not product:
            print('faceing from database')
            queryset=Products.objects.all()
            serializer=ProductSerializer(queryset,many=True)
            product=serializer.data
            cache.set('all_products',product,timeout=60)
        else:
            print("faceing from redis cache")
        return Response(product)
    

from celery_webSoket.celery import add


def index(request):
    print("Task started...")
    result = add.delay(10, 20)  # arguments দেওয়া আছে
    print("Task ID:", result.id)
    return render(request, 'home.html')