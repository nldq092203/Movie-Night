# Base image
FROM python:3.9-slim

# Create a non-root user and group
RUN addgroup --system celerygroup && adduser --system --ingroup celerygroup celeryuser

# Set the working directory
WORKDIR /app

# Copy project files to the container
COPY ../../ .

# Change ownership of the application files to the non-root user
RUN chown -R celeryuser:celerygroup /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to the non-root user
USER celeryuser

# Expose the application port
EXPOSE 8000

# Default command (will be overridden by Railway's start command)
CMD ["gunicorn", "movienight.wsgi:application", "--bind", "0.0.0.0:8000"]