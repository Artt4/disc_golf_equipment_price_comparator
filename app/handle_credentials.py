import os
from dotenv import load_dotenv
from google.cloud import secretmanager

def get_secret(secret_name):
    app_env = os.getenv('APP_ENV', 'local').lower()
    
    if app_env == 'local':
        load_dotenv()
        value = os.getenv(secret_name)
        if not value:
            raise ValueError(f"Local secret {secret_name} not found in .env")
        return value
        
    elif app_env == 'prod':
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        if not project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set")
            
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(name=secret_path)
        return response.payload.data.decode('UTF-8')