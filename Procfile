web: gunicorn tp_django.wsgi
web: python manage.py collectstatic --noinput && gunicorn tp_django.wsgi