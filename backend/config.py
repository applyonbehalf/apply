# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    def __init__(self):
        # Database
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY") 
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        
        # Authentication
        self.jwt_secret = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-this-in-production")
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24 * 7  # 7 days
        
        # AI Services
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Application
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "True").lower() == "true"
        
        # Redis
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Validate required settings
        if not self.supabase_url:
            raise ValueError("SUPABASE_URL is required")
        if not self.supabase_service_key:
            raise ValueError("SUPABASE_SERVICE_KEY is required")

# Create global settings instance
settings = Settings()