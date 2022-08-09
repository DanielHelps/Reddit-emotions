web: bin/start-pgbouncer python manage.py runserver 0.0.0.0:\$PORT
release: python manage.py migrate
celery: -A reddit_emotions worker -l info --pool=solo
celerybeat: -A reddit_emotions beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
