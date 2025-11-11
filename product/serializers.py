from rest_framework import serializers
from .models import Products
from .models import Mail

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Products
        fields='__all__'
        

class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = '__all__'