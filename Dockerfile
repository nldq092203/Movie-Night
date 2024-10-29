# Base image
FROM python:3.9-slim

# Create a non-root user
RUN adduser --disabled-password --gecos '' myuser

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Change ownership of the app directory
RUN chown -R myuser:myuser /app

# Switch to the non-root user
USER myuser

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install supervisor (as root)
USER root
RUN apt-get update && apt-get install -y supervisor && apt-get clean

# Switch back to non-root user
USER myuser

# Copy the supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the port for Django
EXPOSE 8000

# Start supervisor to manage all services
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]