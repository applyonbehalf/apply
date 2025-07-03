# ultra_simple.py - Create this file in your backend directory
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="IntelliApply Test")

@app.get("/")
def root():
    return {"message": "Hello from IntelliApply!", "status": "working"}

@app.get("/health")
def health():
    return {"status": "healthy", "message": "API is running"}

@app.get("/test")
def test():
    return {"test": "passed", "conda": "working"}

if __name__ == "__main__":
    print("🚀 Starting ultra-simple FastAPI test...")
    print("Visit: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="localhost", port=8000, log_level="info")