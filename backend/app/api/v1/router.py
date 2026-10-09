from fastapi import APIRouter

from app.api.v1 import health, scans, webhooks

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(scans.router, tags=["scans"])
api_router.include_router(webhooks.router, tags=["webhooks"])
