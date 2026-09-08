from fastapi import FastAPI
from backend.auth.routes import router as auth_router

app = FastAPI(
    title="Innovation Procurement Bridge API",
    version="1.0.0"
)

# Include Authentication Routes
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "API is running..."}