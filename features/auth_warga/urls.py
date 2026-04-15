# features/auth_warga/urls.py

from django.urls import path

from features.auth_warga.views import (
    activate_user_view,
    create_admin_user_view,
    create_warga_user_view,
    deactivate_user_view,
    login_view,
    logout_view,
    me_view,
)

urlpatterns = [
    path("login/", login_view, name="auth-login"),
    path("logout/", logout_view, name="auth-logout"),
    path("me/", me_view, name="auth-me"),
    path("users/warga/create/", create_warga_user_view, name="auth-create-warga-user"),
    path("users/admin/create/", create_admin_user_view, name="auth-create-admin-user"),
    path("users/<uuid:user_id>/activate/", activate_user_view, name="auth-activate-user"),
    path("users/<uuid:user_id>/deactivate/", deactivate_user_view, name="auth-deactivate-user"),
]