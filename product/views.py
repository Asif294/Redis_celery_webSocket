from django.shortcuts import render
from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from .models import Products
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MailSerializer
from .tasks import send_email_task


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
    




class SendMailAPIView(APIView):
    def post(self, request):
        serializer = MailSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data['title']
            body = serializer.validated_data['body']
            recipient = serializer.validated_data['recipient']
            # Celery task call
            send_email_task.delay(title, body, recipient)
            return Response({"message": "Email is being sent in background"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


