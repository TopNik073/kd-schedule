import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.logging import get_logger

logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    Logs information about the request, execution time, and response status.
    """
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        logger.info(
            f"Request started   | ID: {request_id} | "
            f"{request.method} {request.url.path}"
        )
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            logger.info(
                f"Request completed | ID: {request_id} | "
                f"Status: {response.status_code} | "
                f"Time: {process_time:.4f}s"
            )
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}s"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed | ID: {request_id} | "
                f"Error: {str(e)} | "
                f"Time: {process_time:.4f}s",
                exc_info=e
            )
            
            raise
