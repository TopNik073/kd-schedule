import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.grpc.server import GRPCServer

from src.core.config import settings
from src.core.logger import get_logger
from src.core.middleware import RequestLoggingMiddleware

from src.api.v1 import v1_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    base_path = f"http://{settings.APP_HOST}:{settings.APP_PORT}"
    logger.info(f"API server started on {base_path}")
    logger.info(f"OpenAPI docs: {base_path}/docs")
    grpc_server = GRPCServer(settings.GRPC_SERVER_PORT)
    asyncio.create_task(grpc_server.start())
    yield
    logger.warning("Stopping app...")
    await grpc_server.stop()


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT, log_level=40)
    logger.warning("API server stopped")
