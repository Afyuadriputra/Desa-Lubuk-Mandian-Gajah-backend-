# features/auth_warga/api.py
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from ninja.errors import HttpError
from ninja import Query, Router
from ninja.utils import check_csrf
from .schemas import (
    ActivationOut,
    ChangePasswordIn,
    CsrfTokenOut,
    CreateAdminIn,
    CreateWargaIn,
    GroupOut,
    LoginIn,
    PermissionFlatOut,
    PermissionGroupOut,
    PermissionOut,
    UpdateUserIn,
    UserDetailOut,
    UserListQueryIn,
    UserOut,
)
from .services import AuthService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Autentikasi & Akun"])
auth_service = AuthService()

@router.get("/csrf", auth=None, response=CsrfTokenOut, url_name="auth-csrf")
def csrf_token_api(request):
    return {"csrfToken": get_token(request)}


@router.post("/login", url_name="auth-login", response={200: UserOut})
def login_api(request, payload: LoginIn):
    csrf_error = check_csrf(request, login_api)
    if csrf_error:
        raise HttpError(403, "CSRF verification failed.")

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


@router.get(
    "/users",
    auth=AuthAdminOnly,
    response=list[UserOut],
    url_name="auth-users-list",
)
def list_users_api(request, filters: UserListQueryIn = Query(...)):
    return auth_service.list_users(
        actor=request.user,
        q=filters.q,
        role=filters.role,
        is_active=filters.is_active,
    )


@router.get(
    "/users/{user_id}",
    auth=AuthActiveUser,
    response=UserDetailOut,
    url_name="auth-users-detail",
)
def get_user_detail_api(request, user_id: str):
    return auth_service.get_user_detail(request.user, user_id)


@router.put(
    "/users/{user_id}",
    auth=AuthActiveUser,
    response=UserDetailOut,
    url_name="auth-users-update",
)
def update_user_api(request, user_id: str, payload: UpdateUserIn):
    return auth_service.update_user(
        request.user,
        user_id,
        nama_lengkap=payload.nama_lengkap,
        nomor_hp=payload.nomor_hp,
        role=payload.role,
        is_active=payload.is_active,
        is_staff=payload.is_staff,
        is_superuser=payload.is_superuser,
        groups=payload.groups,
        user_permissions=payload.user_permissions,
    )


@router.get(
    "/groups",
    auth=AuthActiveUser,
    response=list[GroupOut],
    url_name="auth-groups-list",
)
def list_groups_api(request):
    return auth_service.list_groups(request.user)


@router.get(
    "/permissions",
    auth=AuthActiveUser,
    response=list[PermissionGroupOut],
    url_name="auth-permissions-list",
)
def list_permissions_api(request):
    permissions = auth_service.list_permissions(request.user)
    grouped: dict[tuple[str, str], list] = {}
    for permission in permissions:
        key = (permission.content_type.app_label, permission.content_type.model)
        grouped.setdefault(key, []).append(permission)

    return [
        PermissionGroupOut(
            app_label=app_label,
            model=model,
            permissions=[
                PermissionFlatOut(
                    id=permission.id,
                    app_label=permission.content_type.app_label,
                    model=permission.content_type.model,
                    codename=permission.codename,
                    name=permission.name,
                )
                for permission in items
            ],
        )
        for (app_label, model), items in grouped.items()
    ]

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
