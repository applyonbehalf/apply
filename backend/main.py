# main.py - Updated FastAPI app with bot endpoints
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Create FastAPI app first
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

# Import API routers after app creation to avoid circular imports
try:
    from api import auth, users, profiles, applications, batches, captcha, bot
    
    # Include API routers
    app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
    app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
    app.include_router(batches.router, prefix="/api/batches", tags=["batches"])
    app.include_router(captcha.router, prefix="/api/captcha", tags=["captcha"])
    app.include_router(bot.router, prefix="/api/bot", tags=["bot-control"])  # New bot endpoints
    
    print("✅ All API routers loaded successfully")
    
except ImportError as e:
    print(f"⚠️ Warning: Could not import API routers: {e}")
    print("API endpoints will not be available")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "IntelliApply API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to IntelliApply API v7.0",
        "version": "1.0.0",
        "features": [
            "Multi-user job applications",
            "AI-powered form filling", 
            "CAPTCHA handling",
            "Real-time processing",
            "Application queue management"
        ],
        "docs": "/docs"
    }

# Bot status endpoint (quick check)
@app.get("/bot-status")
async def quick_bot_status():
    """Quick bot status check (no auth required)"""
    try:
        from services.bot_service import bot_service
        status = await bot_service.get_bot_status()
        return {
            "running": status.get('running', False),
            "active_applications": status.get('stats', {}).get('applications_processed', 0),
            "success_rate": status.get('stats', {}).get('success_rate', 0)
        }
    except Exception as e:
        return {"running": False, "error": "Unable to get status"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"Global exception: {exc}")
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