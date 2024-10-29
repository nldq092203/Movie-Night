# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and switch to that user
RUN adduser --disabled-password celeryuser
USER celeryuser

# Expose the application port
EXPOSE 8000

# Run the command
CMD ["sh", "-c", "gunicorn movienight.wsgi:application --bind 0.0.0.0:8000"]