web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:${PORT:-8000}
create_superuser: python create_superuser.py