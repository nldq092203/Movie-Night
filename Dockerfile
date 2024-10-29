# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8000

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py migrate && gunicorn movienight.wsgi:application --bind 0.0.0.0:8000"]