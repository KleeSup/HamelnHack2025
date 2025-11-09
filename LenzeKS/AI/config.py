import os
from pathlib import Path
from dotenv import load_dotenv

# Lade .env Datei
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    """Zentrale Konfiguration aus Environment Variables"""
    
    # Azure OpenAI
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_EMBEDDING = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    
    # Azure Postgres
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
