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


# Copy the requirements file into the container
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uwsgi

# Copy the application code into the container
COPY . /usr/src/app/

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=project.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/app

# Collect static files
RUN python manage.py collectstatic --noinput

# Set proper permissions
RUN chown -R www-data:www-data /usr/src/app /var/log/uwsgi
RUN chmod -R 755 /usr/src/app


# Expose port for uWSGI/Django
EXPOSE 8001

# Create supervisor directory and copy configuration
RUN mkdir -p /etc/supervisor/conf.d
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run Supervisor to manage processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 