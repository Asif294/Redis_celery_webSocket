from celery import shared_task

import time

@shared_task
def send_welcome_email(username):
    print(f"Sending welcome email to {username}...")
    time.sleep(5)  
    print(f"Email sent to {username} ✅")
    return f"Email sent successfully to {username}"
