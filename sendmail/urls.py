from django.urls import path,include
from .views import SendMailAPIView
from .import views
urlpatterns = [
   
   path('send-mail/', SendMailAPIView.as_view(), name='send-mail'),
   
]