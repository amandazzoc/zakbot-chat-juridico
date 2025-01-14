import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
    
    @classmethod
    def validate_config(cls):
        """Validate that required environment variables are set"""
        if not cls.TELEGRAM_TOKEN or not cls.BUCKET_NAME:
            raise ValueError("Por favor, configure as variáveis de ambiente TELEGRAM_BOT_TOKEN e AWS_BUCKET_NAME")