FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed for Playwright Chromium only
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libasound2 libxshmfence1 libxss1 libxtst6 \
    fonts-liberation xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY scraper_service/run_scraper.py /app/run_scraper.py
COPY app /app/app
COPY .env /app/.env

# Install Python dependencies (including Playwright)
RUN pip install --no-cache-dir -r app/requirements.txt && \
    pip install --no-cache-dir playwright

# Preinstall Chromium only (avoids timeout issues for Firefox/WebKit)
RUN python -m playwright install chromium

# Default command when the container starts
CMD ["python", "run_scraper.py"]
