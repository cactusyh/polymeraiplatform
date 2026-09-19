"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router as api_router
from backend.app.api.chemistry import router as chemistry_router
from backend.app.api.predictions import router as prediction_router
from backend.app.core.config import settings
app=FastAPI(title=settings.app_name,version=settings.app_version)
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=["GET","POST","PATCH"],allow_headers=["*"])
@app.get("/health",tags=["health"])
def health()->dict[str,str]:return {"status":"ok","service":"polymer-ai-backend"}
app.include_router(api_router)
app.include_router(chemistry_router)
app.include_router(prediction_router)
