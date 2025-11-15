from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from .models import Products
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



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
    





