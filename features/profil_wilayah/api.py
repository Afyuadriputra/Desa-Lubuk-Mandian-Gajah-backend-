# features/profil_wilayah/api.py

from ninja import Router, Form, File
from ninja.files import UploadedFile

from .schemas import (
    TambahDusunIn, 
    TambahPerangkatIn, 
    UpdateProfilDesaIn,
    DusunOut, 
    ProfilPublikAggregatedOut,
    ProfilDesaOut
)
from .services import DusunService, PerangkatService, ProfilDesaService
from toolbox.api.auth import AuthAdminOnly

router = Router(tags=["Profil Wilayah"])

# Dependency Inversion Principle (DIP)
dusun_service = DusunService()
perangkat_service = PerangkatService()
profil_service = ProfilDesaService()


@router.get("/publik", response=ProfilPublikAggregatedOut)
def profil_publik_api(request):
    """
    Endpoint terbuka tanpa Auth. 
    Menggabungkan Visi/Misi dan list Perangkat Desa dalam satu panggilan.
    """
    profil = profil_service.get_profil()
    perangkat = perangkat_service.get_perangkat_publik()
    
    return {
        "profil": profil,
        "perangkat": list(perangkat)
    }


@router.post("/admin/dusun", auth=AuthAdminOnly, response={201: DusunOut})
def tambah_dusun_api(request, payload: TambahDusunIn):
    """Hanya Admin/Superadmin yang bisa menambah dusun."""
    dusun = dusun_service.tambah_dusun(
        actor=request.user, 
        nama_dusun=payload.nama_dusun, 
        kepala_dusun=payload.kepala_dusun
    )
    return 201, dusun


@router.post("/admin/perangkat", auth=AuthAdminOnly, response={201: dict})
def tambah_perangkat_api(
    request, 
    payload: Form[TambahPerangkatIn], 
    foto: File[UploadedFile] = None
):
    """Menambah data perangkat desa beserta fotonya."""
    perangkat = perangkat_service.tambah_perangkat(
        actor=request.user,
        user_id=payload.user_id,
        jabatan=payload.jabatan,
        is_published=payload.is_published,
        foto=foto
    )
    return 201, {"detail": "Perangkat berhasil ditambahkan", "id": perangkat.id}


@router.put("/admin/profil", auth=AuthAdminOnly, response=ProfilDesaOut)
def update_profil_desa_api(request, payload: UpdateProfilDesaIn):
    """
    Update data Visi, Misi, dan Sejarah (Singleton).
    Input HTML aman karena menggunakan SafeHTMLString di schema.
    """
    profil = profil_service.perbarui_profil(
        actor=request.user,
        visi=payload.visi,
        misi=payload.misi,
        sejarah=payload.sejarah
    )
    return profil