from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_email_task(title, body, recipient):
    send_mail(
        subject=title,
        message=body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient],
        fail_silently=False,
    )
    return "Email sent"
