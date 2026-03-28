FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=placeholder-for-build \
    DATABASE_URL=postgres://placeholder/placeholder \
    FRONTEND_URL=http://placeholder \
    RESEND_API_KEY=placeholder \
    python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD sh -c "python manage.py migrate && \
           python manage.py createcachetable && \
           python manage.py create_superuser_if_none && \
           gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120"