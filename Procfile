web: gunicorn movienight.wsgi:application --bind 0.0.0.0:8000
celery: celery -A movienight worker --loglevel=INFO --concurrency=4
celery-beat: celery -A movienight beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler