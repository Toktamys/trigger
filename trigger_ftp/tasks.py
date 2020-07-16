from __future__ import absolute_import, unicode_literals

from celery import shared_task
from trigger_ftp.services import FTPHandler


@shared_task
def fetch_crm_data_from_ftp():
    try:
        handler = FTPHandler()
        handler.save()
    except Exception as error:
        print("error 13", str(error))
