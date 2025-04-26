from sys import exc_info

import grpc
import time
import uuid

from src.core.logger import get_logger

logger = get_logger(__name__)


class LoggingInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_details):
        trace_id: str = str(uuid.uuid4())
        context = {"context": {"trace_id": trace_id, "method": handler_details.method}}
        logger.info(f"Received gRPC request", extra=context)
        try:
            start_time = time.perf_counter()
            response = await continuation(handler_details)
            duration = time.perf_counter() - start_time
            context["context"]["process_time"] = f"{duration:.6f}"
            logger.info(f"gRPC request completed", extra=context)
            return response
        except Exception as e:
            logger.error(f"gRPC request failed", extra=context, exc_info=e)
            raise
