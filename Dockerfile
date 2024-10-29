# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install supervisor to manage multiple processes
RUN apt-get update && apt-get install -y supervisor && apt-get clean

# Copy the application code
COPY . .

# Copy the supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create a directory for logs (if using custom log paths in supervisord.conf)
RUN mkdir -p /app/logs

# Expose the port for Django
EXPOSE 8000

# Start supervisor to manage all services
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]