# toolbox/logging/request_context.py

import uuid
from contextvars import ContextVar

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
request_path_ctx: ContextVar[str | None] = ContextVar("request_path", default=None)
request_method_ctx: ContextVar[str | None] = ContextVar("request_method", default=None)


def generate_request_id() -> str:
    return str(uuid.uuid4())


def set_request_context(
    request_id: str | None = None,
    user_id: str | int | None = None,
    path: str | None = None,
    method: str | None = None,
) -> None:
    request_id_ctx.set(request_id or generate_request_id())
    user_id_ctx.set(str(user_id) if user_id is not None else None)
    request_path_ctx.set(path)
    request_method_ctx.set(method)


def get_request_id() -> str | None:
    return request_id_ctx.get()


def get_user_id() -> str | None:
    return user_id_ctx.get()


def get_request_path() -> str | None:
    return request_path_ctx.get()


def get_request_method() -> str | None:
    return request_method_ctx.get()


def get_request_context() -> dict[str, str | None]:
    return {
        "request_id": get_request_id(),
        "user_id": get_user_id(),
        "path": get_request_path(),
        "method": get_request_method(),
    }


def clear_request_context() -> None:
    request_id_ctx.set(None)
    user_id_ctx.set(None)
    request_path_ctx.set(None)
    request_method_ctx.set(None)