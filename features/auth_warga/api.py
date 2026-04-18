# features/auth_warga/api.py
from django.contrib.auth import login, logout
from ninja import Router
from .schemas import (
    ActivationOut,
    ChangePasswordIn,
    CreateAdminIn,
    CreateWargaIn,
    LoginIn,
    UserOut,
)
from .services import AuthService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Autentikasi & Akun"])
auth_service = AuthService()

@router.post("/login", url_name="auth-login", response={200: UserOut})
def login_api(request, payload: LoginIn):
    result = auth_service.login_user(request, payload.nik, payload.password)
    login(request, result.user)
    return result.user

@router.post("/logout", auth=AuthActiveUser, url_name="auth-logout")
def logout_api(request):
    logout(request)
    return {"detail": "Logout berhasil."}

@router.get("/me", auth=AuthActiveUser, response=UserOut, url_name="auth-me")
def me_api(request):
    return request.user

@router.post(
    "/users/warga/create",
    auth=AuthAdminOnly,
    response={201: UserOut},
    url_name="auth-users-warga-create",
)
def create_warga_api(request, payload: CreateWargaIn):
    user = auth_service.create_warga_account(
        actor=request.user,
        **payload.dict()
    )
    return 201, user


@router.post(
    "/users/admin/create",
    auth=AuthAdminOnly,
    response={201: UserOut},
    url_name="auth-users-admin-create",
)
def create_admin_api(request, payload: CreateAdminIn):
    user = auth_service.create_admin_account(
        actor=request.user,
        **payload.dict()
    )
    return 201, user


@router.post(
    "/users/{user_id}/activate",
    auth=AuthAdminOnly,
    response=ActivationOut,
    url_name="auth-users-activate",
)
def activate_user_api(request, user_id: str):
    return auth_service.activate_account(request.user, user_id)


@router.post(
    "/users/{user_id}/deactivate",
    auth=AuthAdminOnly,
    response=ActivationOut,
    url_name="auth-users-deactivate",
)
def deactivate_user_api(request, user_id: str):
    return auth_service.deactivate_account(request.user, user_id)


@router.post(
    "/change-password",
    auth=AuthActiveUser,
    response=UserOut,
    url_name="auth-change-password",
)
def change_password_api(request, payload: ChangePasswordIn):
    return auth_service.change_password(
        actor=request.user,
        current_password=payload.current_password,
        new_password=payload.new_password,
        confirm_password=payload.confirm_password,
    )
