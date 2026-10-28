from fastapi import APIRouter

from app.api.v1.feedback import router as feedback_router
from app.api.v1.findings import router as findings_router
from app.api.v1.health import router as health_router
from app.api.v1.pull_requests import router as pull_requests_router
from app.api.v1.repositories import router as repositories_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.settings import router as settings_router
from app.api.v1.webhooks import router as webhooks_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(repositories_router)
api_v1_router.include_router(pull_requests_router)
api_v1_router.include_router(reviews_router)
api_v1_router.include_router(findings_router)
api_v1_router.include_router(feedback_router)
api_v1_router.include_router(webhooks_router)
api_v1_router.include_router(settings_router)
