# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies for building Python libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    libpcre3 \
    libpcre3-dev \
    libssl-dev \
    libffi-dev \
    supervisor \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/* 

# Create necessary directories
RUN mkdir -p /usr/src/app/static /usr/src/app/staticfiles /usr/src/app/media /var/log/uwsgi

# Copy the requirements file into the container
COPY requirements.txt /usr/src/app/
RUN ls -la /usr/src/app/requirements.txt

# Install Python dependencies with binary wheels
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt
RUN pip install --no-cache-dir uwsgi

# Copy the application code into the container
COPY . /usr/src/app/
RUN ls -la /usr/src/app/

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=project.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/app
ENV USE_S3=False

# Collect static files using local storage
RUN python manage.py collectstatic --noinput

# Set proper permissions
RUN chown -R www-data:www-data /usr/src/app /var/log/uwsgi && \
    chmod -R 755 /usr/src/app

# Create supervisor directory and copy configuration
RUN mkdir -p /etc/supervisor/conf.d
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN ls -la /etc/supervisor/conf.d/supervisord.conf

# Create entrypoint script for S3 upload
RUN echo '#!/bin/bash\n\
if [ "$USE_S3" = "true" ]; then\n\
    echo "Uploading static files to S3..."\n\
    python manage.py collectstatic --noinput --clear\n\
fi\n\
exec "$@"' > /usr/src/app/docker-entrypoint.sh && \
    chmod +x /usr/src/app/docker-entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]

# Run Supervisor to manage processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 