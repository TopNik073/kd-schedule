import grpc
import time

from src.core.logging import get_logger

logger = get_logger(__name__)

class LoggingInterceptor(grpc.aio.ServerInterceptor):
	async def intercept_service(self, continuation, handler_details):
		logger.info(f"Received request: {handler_details.method}")
		try:
			start_time = time.perf_counter()
			response = await continuation(handler_details)
			duration = time.perf_counter() - start_time
			logger.info(f"Response for {handler_details.method} completed in {duration:.6f} seconds")
			return response
		except Exception as e:
			logger.error(f"Error in {handler_details.method}: {e}")
			raise
