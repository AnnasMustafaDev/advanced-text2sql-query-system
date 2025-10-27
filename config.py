"""
Configuration settings for the World Bank SQL Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/world_bank_data_updated.db')
    SQLALCHEMY_DATABASE_URL = f'sqlite:///{DATABASE_PATH}'
    
    # Few-shot examples path
    FEW_SHOTS_JSON_PATH = os.getenv('FEW_SHOTS_JSON_PATH', 'data/Worldbankfewshots.json')
    
    # Model configuration
    CHAT_MODEL = os.getenv('CHAT_MODEL', 'gpt-4o')
    SUMMARY_MODEL = os.getenv('SUMMARY_MODEL', 'gpt-4o-mini')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))
    
    # Indicator search configuration
    TOP_N_INDICATORS = int(os.getenv('TOP_N_INDICATORS', '5'))
    
    # Query limits
    DEFAULT_LIMIT = int(os.getenv('DEFAULT_LIMIT', '150'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in .env file")
        return True