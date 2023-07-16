import os
from celery import Celery

# standart code for Celery in Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fabrique_test_case.settings')
app = Celery('fabrique_test_case')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
