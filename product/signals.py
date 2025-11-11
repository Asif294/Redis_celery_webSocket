from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Mail
from .tasks import send_email_task


@receiver(post_save, sender=Mail)
def send_mail_to_users(sender, instance, created, **kwargs):
    if created:
        if instance.receiver: 
            if instance.receiver.email:
                send_email_task.delay(
                    title=instance.subject,
                    body=instance.body,
                    recipient=instance.receiver.email
                )
        else: 
            users = User.objects.all()
            for user in users:
                if user.email:
                    send_email_task.delay(
                        title=instance.subject,
                        body=instance.body,
                        recipient=user.email
                    )

                   
