from typing import Any, Callable

import grpc
import time
import uuid

from src.core.logger import get_logger

logger = get_logger(__name__)


class LoggingInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_details):
        trace_id: str = str(uuid.uuid4())
        context = {"trace_id": trace_id, "method": handler_details.method}
        await logger.ainfo(f"Received gRPC request", context=context)
        try:
            start_time = time.perf_counter()
            response = await continuation(handler_details)
            duration = time.perf_counter() - start_time
            context["process_time"] = f"{duration:.6f}"
            await logger.ainfo(f"gRPC request completed", context=context)
            return response
        except Exception as e:
            await logger.aerror(f"gRPC request failed", context=context, exc_info=e)
            raise
