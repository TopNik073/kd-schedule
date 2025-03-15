from sys import prefix

from fastapi import APIRouter

from src.api.v1.schedule.router import router as schedule_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(schedule_router)
