FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY recommender.py .
COPY handle_credentials.py .
COPY handle_db_connections.py .
COPY requirements.txt .

CMD ["python", "recommender.py"]