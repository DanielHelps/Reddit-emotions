# import django
# django.setup()

from django.db import models
import main.emotion_check


# main.emotion_check.import_classifier()
# main.emotion_check.import_top_100()

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)