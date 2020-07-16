from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trigger.settings')

app = Celery('trigger')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(None)


@app.task(bind=True)
def debug_task(self):
    print('Requesdfsdfst: {0!r}'.format(self.request))
