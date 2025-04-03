FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed for Playwright Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy app files from the parent directory to the container's /app directory
COPY /scraper_service/run_scraper.py /app/run_scraper.py
COPY app ./app
COPY .env .env

# Install Python dependencies including Playwright
RUN pip install --no-cache-dir -r app/requirements.txt

# Install Playwright (but NOT the browsers yet)
RUN pip install playwright

# At container runtime: install browsers, then run scraper
CMD ["sh", "-c", "python -m playwright install --with-deps && python run_scraper.py"]
