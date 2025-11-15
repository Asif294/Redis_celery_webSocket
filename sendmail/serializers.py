from .models import Mail
from rest_framework import serializers
class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = '__all__'