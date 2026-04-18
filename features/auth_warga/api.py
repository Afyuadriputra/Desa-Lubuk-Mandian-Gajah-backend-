# features/auth_warga/api.py
from django.contrib.auth import login, logout
from ninja import Router
from .schemas import LoginIn, UserOut, CreateWargaIn
from .services import AuthService
from toolbox.api.auth import AuthActiveUser, AuthAdminOnly

router = Router(tags=["Autentikasi & Akun"])
auth_service = AuthService()

@router.post("/login", response={200: UserOut})
def login_api(request, payload: LoginIn):
    result = auth_service.login_user(request, payload.nik, payload.password)
    login(request, result.user)
    return result.user

@router.post("/logout", auth=AuthActiveUser)
def logout_api(request):
    logout(request)
    return {"detail": "Logout berhasil."}

@router.get("/me", auth=AuthActiveUser, response=UserOut)
def me_api(request):
    return request.user

@router.post("/users/warga/create", auth=AuthAdminOnly, response={201: UserOut})
def create_warga_api(request, payload: CreateWargaIn):
    user = auth_service.create_warga_account(
        actor=request.user,
        **payload.dict()
    )
    return 201, user