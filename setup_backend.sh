#!/bin/bash
# setup_backend.sh - Create the FastAPI backend structure

echo "🚀 Setting up IntelliApply Backend Structure..."

# Create main backend directory
mkdir -p backend
cd backend

# Create directory structure
mkdir -p {database,auth,api,services,bot,utils,workers}

# Create __init__.py files
touch database/__init__.py
touch auth/__init__.py
touch api/__init__.py
touch services/__init__.py
touch bot/__init__.py
touch utils/__init__.py
touch workers/__init__.py

echo "✅ Created directory structure"

# Create requirements.txt
cat > requirements.txt << 'EOF'
# FastAPI and server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
supabase==2.3.4
asyncpg==0.29.0
sqlalchemy==2.0.23

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Background tasks
celery==5.3.4
redis==5.0.1

# Bot dependencies (your existing ones)
selenium==4.15.2
webdriver-manager==4.0.1
google-generativeai==0.3.2
anthropic==0.7.8
pypdf==3.17.4

# Notifications
twilio==8.10.0
sendgrid==6.11.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
pillow==10.1.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
EOF

echo "✅ Created requirements.txt"

# Create main config file
cat > config.py << 'EOF'
# config.py
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    database_url: str
    
    # Authentication
    jwt_secret: str = "your-super-secret-jwt-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # AI Services
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Notifications
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    
    # Application
    environment: str = "development"
    debug: bool = True
    
    # Redis (for background tasks)
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

# Create global settings instance
settings = Settings()
EOF

echo "✅ Created config.py"

# Create main FastAPI app
cat > main.py << 'EOF'
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import API routers
from api import auth, users, profiles, applications, batches, captcha

# Create FastAPI app
app = FastAPI(
    title="IntelliApply API",
    description="Multi-user job application automation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://applyonbehalf.com", "https://*.applyonbehalf.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(batches.router, prefix="/api/batches", tags=["batches"])
app.include_router(captcha.router, prefix="/api/captcha", tags=["captcha"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "IntelliApply API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to IntelliApply API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
EOF

echo "✅ Created main.py"

echo "📁 Backend structure created successfully!"
echo ""
echo "Next steps:"
echo "1. cd backend"
echo "2. pip install -r requirements.txt"
echo "3. Copy your .env file to backend directory"
echo "4. Run the next setup script"
EOF