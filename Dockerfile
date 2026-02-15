# 1. Start with an official Python base image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies, including the PHP command-line interpreter
# and necessary extensions (curl for web requests, json for processing).
RUN apt-get update && apt-get install -y \
    php-cli \
    php-curl \
    php-json \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 4. Copy the Python requirements file first to leverage Docker layer caching
COPY requirements.txt requirements.txt

# 5. Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all your application files into the container
COPY . .

# 7. Expose the port (Railway sets PORT dynamically, 8080 is default)
EXPOSE 8080

# 8. Define the command to run the application using Gunicorn (a production-ready server)
# - gthread worker handles concurrent requests without blocking
# - timeout 120 covers long PHP subprocess runs
# - keep-alive 5 prevents idle socket timeouts that kill workers
# - graceful-timeout lets workers finish current requests on restart
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --timeout 120 --graceful-timeout 30 --keep-alive 5 --workers 2 --threads 4 --worker-class gthread app:app"]
