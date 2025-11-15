from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MailSerializer
from .tasks import send_email_task

class SendMailAPIView(APIView):
    def post(self, request):
        serializer = MailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(
                {"message": "Mail created and sending started in background."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)