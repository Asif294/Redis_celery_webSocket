from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
@shared_task
def send_email_task(subject, body, recipient, mail_type='alert'):
    template_name = f'email_template/{mail_type}.html'
    
    html_content = render_to_string(template_name, {
        'subject': subject,
        'body': body,
    })
    email = EmailMultiAlternatives(
        subject=subject,
        body="", 
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
    return f"Email sent to {recipient}"