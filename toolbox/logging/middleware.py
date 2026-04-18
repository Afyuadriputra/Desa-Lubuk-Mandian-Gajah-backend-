# toolbox/logging/middleware.py
from asgiref.sync import iscoroutinefunction
from toolbox.logging.request_context import (
    clear_request_context, generate_request_id, set_request_context
)

class RequestContextMiddleware:
    REQUEST_ID_HEADER = "X-Request-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if iscoroutinefunction(self.get_response):
            return self.__acall__(request)
        return self.__sync_call__(request)

    def _setup_context(self, request):
        request_id = request.headers.get(self.REQUEST_ID_HEADER) or generate_request_id()
        user_id = None
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            user_id = getattr(user, "id", None)
        set_request_context(request_id=request_id, user_id=user_id, path=request.path, method=request.method)
        return request_id

    def __sync_call__(self, request):
        request_id = self._setup_context(request)
        try:
            response = self.get_response(request)
            response[self.REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_request_context()

    async def __acall__(self, request):
        request_id = self._setup_context(request)
        try:
            response = await self.get_response(request)
            response[self.REQUEST_ID_HEADER] = request_id
            return response
        finally:
            clear_request_context()