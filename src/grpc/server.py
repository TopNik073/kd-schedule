import grpc

from src.core.logging import get_logger
from src.grpc.interceptors import LoggingInterceptor

logger = get_logger(__name__)


class GRPCServer:
    def __init__(self, port: int):
        self.port = port
        self.server = grpc.aio.server(interceptors=[LoggingInterceptor()])

    async def start(self):
        self.server.add_insecure_port(f"[::]:{self.port}")
        await self.server.start()
        logger.info(f"gRPC server started on port {self.port}")

    async def stop(self):
        await self.server.stop(None)
        logger.warning("gRPC server stopped")
