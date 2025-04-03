# Use the lighter 'slim' variant of Python 3.10
FROM python:3.10-slim

WORKDIR /app

# Install minimal system dependencies for Playwright to run
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libglib2.0-0 \
    libasound2 \
    libxrandr2 \
    libxdamage1 \
    libatk-bridge2.0-0 \
    libgbm1 \
    fonts-liberation \
    xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY scraper_service/run_scraper.py .
COPY app ./app
COPY .env .

# Install Python dependencies
RUN pip install --no-cache-dir -r app/requirements.txt
RUN pip install --no-cache-dir playwright

# Install just Chromium (you don’t need Firefox/WebKit)
RUN python -m playwright install chromium

ENV APP_ENV=local

CMD ["python", "run_scraper.py"]