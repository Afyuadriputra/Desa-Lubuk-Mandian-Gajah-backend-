# toolbox/api/auth.py
from django.http import HttpRequest
from ninja.security import django_auth
from toolbox.security.auth import is_active_user, is_internal_admin

def AuthActiveUser(request: HttpRequest):
    """Validasi session login standar"""
    user = django_auth(request)
    if user and is_active_user(request.user):
        return user
    return None

def AuthAdminOnly(request: HttpRequest):
    """Validasi khusus role Admin Desa / Superadmin"""
    user = AuthActiveUser(request)
    if user and is_internal_admin(request.user):
        return user
    return None

# Cara pakai di Router nanti:
# @router.post("/buat/", auth=AuthAdminOnly)