import grpc

from src.core.logger import get_logger
from src.grpc_server.interceptors import LoggingInterceptor
from src.grpc_server.schedule_pb2_grpc import add_ScheduleServiceServicer_to_server
from src.grpc_server.servicers.schedule_servicer import ScheduleServicer

logger = get_logger(__name__)


class GRPCServer:
    def __init__(self, port: int) -> None:
        self.port = port
        self.server = grpc.aio.server(interceptors=[LoggingInterceptor()])
        self.setup_services()

    def setup_services(self) -> None:
        schedule_service = ScheduleServicer()
        add_ScheduleServiceServicer_to_server(schedule_service, self.server)

    async def start(self) -> None:
        try:
            self.server.add_insecure_port(f"[::]:{self.port}")
            await self.server.start()
            logger.info(f"gRPC server started on port {self.port}")
        except Exception as e:
            logger.error(f"Error starting gRPC server: {e}")
            raise e

    async def stop(self) -> None:
        try:
            await self.server.stop(None)
            logger.warning("gRPC server stopped")
        except Exception as e:
            logger.error(f"Error stopping gRPC server: {e}")
            raise e
