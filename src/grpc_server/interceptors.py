from collections.abc import Callable
import time
from typing import Any
import uuid

import grpc

from src.core.logger import get_logger

logger = get_logger(__name__)


class LoggingInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(
        self, continuation: Callable, handler_details: grpc.HandlerCallDetails
    ) -> Any:
        trace_id: str = str(uuid.uuid4())
        context = {"trace_id": trace_id, "method": handler_details.method}
        await logger.ainfo("Received gRPC request", context=context)
        try:
            start_time = time.perf_counter()
            response = await continuation(handler_details)
            duration = time.perf_counter() - start_time
        except Exception as e:
            await logger.aerror("gRPC request failed", context=context, exc_info=e)
            raise
        else:
            context["process_time"] = f"{duration:.6f}"
            await logger.ainfo("gRPC request completed", context=context)
            return response
