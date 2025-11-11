from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_email_task(title, body, recipient):
    html_content = render_to_string('email_template.html', {
        'title': title,
        'body': body,
    })
    email = EmailMultiAlternatives(
        subject=title,
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    return f"Email sent to {recipient}"
