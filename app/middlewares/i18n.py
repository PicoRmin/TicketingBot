from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.enums import Language
from app.i18n.fastapi_utils import resolve_lang


class I18nMiddleware(BaseHTTPMiddleware):
    """
    Resolve language once per request and store on request.state.lang
    for easy access in route handlers.
    """

    async def dispatch(self, request: Request, call_next):
        # Try to read user if present on state (optional pattern)
        user = getattr(request.state, "user", None)
        lang: Language = resolve_lang(request, user)
        request.state.lang = lang
        response: Response = await call_next(request)
        return response


__all__ = ["I18nMiddleware"]

