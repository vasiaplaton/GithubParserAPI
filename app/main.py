"""Entry point for fastAPI APP"""
from fastapi import FastAPI, APIRouter
from app.routes.repositories import router as repositories_router

app = FastAPI(title="Top 100 Repositories API")


api = APIRouter(prefix="/api")
api.include_router(repositories_router)
api.include_router(repositories_router)

app.include_router(api)
# Middleware or startup events can be added here
