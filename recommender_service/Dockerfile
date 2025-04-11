FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install pymysql python-dotenv flask
COPY handle_credentials.py .
COPY handle_db_connections.py .
COPY requirements.txt .
CMD ["python", "recommender.py"]