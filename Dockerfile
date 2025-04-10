# Dockerfile
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy app code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r app/requirements.txt

ENV APP_ENV=prod
ENV GOOGLE_CLOUD_PROJECT=chrome-inkwell-455616-p9
ENV GOOGLE_APPLICATION_CREDENTIALS=sa-key.json

# Start Flask app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.main:app"]
