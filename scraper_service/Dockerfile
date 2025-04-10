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
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libcups2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only necessary files
COPY run_scraper.py .
COPY scrape_stores ./scrape_stores
COPY handle_credentials.py .
COPY handle_db_connections.py .
COPY requirements.txt .
#COPY sa-key.json .


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir playwright

# Install just Chromium (you don’t need Firefox/WebKit)
RUN python -m playwright install chromium

ENV APP_ENV=prod
ENV GOOGLE_CLOUD_PROJECT=chrome-inkwell-455616-p9
#ENV GOOGLE_APPLICATION_CREDENTIALS=/app/sa-key.json

CMD ["python", "run_scraper.py"]