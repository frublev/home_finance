import os
import django

# Указываем настройки проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finance.settings")  # или "config.settings" если settings там
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()  # получаем стандартную модель пользователя

# Берём данные из переменных окружения (или задаём по умолчанию)
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

# Создаём суперпользователя, если его ещё нет
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")