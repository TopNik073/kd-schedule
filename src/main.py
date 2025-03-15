from fastapi import FastAPI

from src.core.config import settings
from src.core.logging import setup_app_logging
from src.core.middleware import RequestLoggingMiddleware

from src.api.v1 import v1_router

setup_app_logging()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
