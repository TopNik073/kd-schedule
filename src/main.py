import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.grpc.server import GRPCServer

from src.core.config import settings
from src.core.logging import setup_app_logging
from src.core.middleware import RequestLoggingMiddleware

from src.api.v1 import v1_router

setup_app_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    grpc_server = GRPCServer(50051)
    asyncio.create_task(grpc_server.start())
    yield
    await grpc_server.stop()


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
