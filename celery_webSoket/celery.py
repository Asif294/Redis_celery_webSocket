from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from time import sleep

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celery_webSoket.settings')

app = Celery('celery_webSoket')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task
def add(x, y):
    sleep(10)
    return x + y
