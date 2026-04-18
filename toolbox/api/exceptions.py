# toolbox/api/exceptions.py
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import NinjaAPI
from toolbox.logging.app_logger import get_logger

logger = get_logger("toolbox.api.exceptions")

def register_exception_handlers(api: NinjaAPI):
    # Menangkap error validasi bawaan Django (misal dari models.py)
    @api.exception_handler(DjangoValidationError)
    def django_validation_error(request, exc):
        return api.create_response(
            request,
            {"detail": exc.messages[0] if hasattr(exc, 'messages') else str(exc)},
            status=400
        )

    # Tangkap PermissionError kustom Anda (bisa disesuaikan dengan Base Class Error Anda)
    @api.exception_handler(Exception)
    def handle_global_exceptions(request, exc):
        exc_name = exc.__class__.__name__
        
        if "Permission" in exc_name or "Access" in exc_name:
            return api.create_response(request, {"detail": str(exc)}, status=403)
            
        if "NotFound" in exc_name:
            return api.create_response(request, {"detail": str(exc)}, status=404)
            
        if "Error" in exc_name: # Domain/Service errors
            return api.create_response(request, {"detail": str(exc)}, status=400)

        # Unhandled Server Error
        logger.opt(exception=exc).error("Unhandled API Exception")
        return api.create_response(request, {"detail": "Terjadi kesalahan internal server."}, status=500)