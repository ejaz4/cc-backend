import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # FastAPI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    DEBUG = os.getenv('FASTAPI_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FASTAPI_HOST', '0.0.0.0')
    PORT = int(os.getenv('FASTAPI_PORT', 8000))
    
    # Database Configuration (Supabase PostgreSQL)
    SUPABASE_URI = os.getenv('SUPABASE_URI')
    SUPABASE_API_KEY = os.getenv('SUPABASE_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')  # Direct PostgreSQL connection string
    
    # If DATABASE_URL is not provided, construct it from Supabase credentials
    if not DATABASE_URL and SUPABASE_URI and SUPABASE_API_KEY:
        # Extract host from Supabase URL and construct PostgreSQL connection
        # Supabase URL format: https://project-ref.supabase.co
        # PostgreSQL connection: postgresql://postgres:[password]@[host]:5432/postgres
        host = SUPABASE_URI.replace('https://', '').replace('.supabase.co', '')
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_API_KEY}@{host}.supabase.co:5432/postgres"
    
    # API Keys
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

    
    # File Storage Configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    AUDIO_FOLDER = os.getenv('AUDIO_FOLDER', 'audio')
    
    # OpenAI Configuration

    
    # ElevenLabs Configuration
    ELEVENLABS_BASE_URL = os.getenv('ELEVENLABS_BASE_URL', 'https://api.elevenlabs.io/v1')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
    CORS_ALLOW_METHODS = os.getenv('CORS_ALLOW_METHODS', '*').split(',')
    CORS_ALLOW_HEADERS = os.getenv('CORS_ALLOW_HEADERS', '*').split(',')
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    # File Upload Limits
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB default
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        required_vars = [
            'SUPABASE_URI',
            'SUPABASE_API_KEY',
            'ELEVENLABS_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', '*']

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SUPABASE_URI = 'test_SUPABASE_URI'
    SUPABASE_API_KEY = 'test_SUPABASE_API_KEY'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 