web: python manage.py runserver
release: python manage.py migrate
celery: celery -A reddit_emotions worker -l info --pool=solo
celerybeat: celery -A reddit_emotions beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
