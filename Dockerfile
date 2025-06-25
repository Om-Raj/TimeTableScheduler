# Use official Python image with Alpine for a smaller image size
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install system dependencies for PostgreSQL and building Python packages
RUN apk update && apk add --no-cache \
    build-base \
    libpq-dev \
    && rm -rf /var/cache/apk/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Run Django development server (you can override this in production)
CMD ["gunicorn", "website.wsgi:application", "--bind", "0.0.0.0:8000"]
