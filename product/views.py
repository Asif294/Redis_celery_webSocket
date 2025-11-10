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
    


from django.http import HttpResponse
from .tasks import send_welcome_email

def register_user(request):
    username = "Asif"
    send_welcome_email.delay(username)  # background এ task run হবে
    return HttpResponse("Registration successful! Email will be sent shortly.")
