import grpc
from src.core.logger import get_logger
from src.grpc.interceptors import LoggingInterceptor
from src.grpc.schedule_pb2_grpc import add_ScheduleServiceServicer_to_server
from src.grpc.servicers.schedule_servicer import ScheduleServicer

logger = get_logger(__name__)


class GRPCServer:
    def __init__(self, port: int):
        self.port = port
        self.server = grpc.aio.server(interceptors=[LoggingInterceptor()])
        self.setup_services()

    def setup_services(self):
        schedule_service = ScheduleServicer()
        add_ScheduleServiceServicer_to_server(schedule_service, self.server)

    async def start(self):
        self.server.add_insecure_port(f"[::]:{self.port}")
        await self.server.start()
        logger.info(f"gRPC server started on port {self.port}")

    async def stop(self):
        await self.server.stop(None)
        logger.warning("gRPC server stopped")
