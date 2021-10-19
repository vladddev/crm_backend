from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from . import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

app = Celery('api')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



app.conf.beat_schedule = {
    'check_materials_orders': {
        'task': 'check_materials_orders',
        'schedule': crontab(minute=1, hour=0, day_of_week='*')
    }
}