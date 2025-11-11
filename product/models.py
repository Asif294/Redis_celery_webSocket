from django.db import models
from django.contrib.auth.models import User 
class Products(models.Model):
    name=models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand=models.CharField(max_length=50)

    def __str__(self):
        return self.name

class MailType(models.TextChoices):
    NEWSLETTER = 'newsletter', 'Newsletter'
    OFFER = 'offer', 'Offer'
    NOTIFICATION = 'notification', 'Notification'
    QUOTE = 'quote', 'Quote'
    CONFIRMATION = 'confirmation', 'Confirmation'
    ALERT = 'alert', 'Alert'


class Mail(models.Model):
    subject = models.CharField(max_length=250)
    body = models.TextField()
    type = models.CharField(max_length=20, choices=MailType.choices, default=MailType.ALERT)
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,
    related_name='mails_received',null=True,blank=True
)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.type})"
