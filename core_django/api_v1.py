from django.conf import settings
from ninja import NinjaAPI
from toolbox.api.exceptions import register_exception_handlers

# Import router dari semua feature Anda
from features.auth_warga.api import router as auth_router
from features.dashboard_admin.api import router as dashboard_router
from features.homepage_konten.api import router as homepage_router
from features.layanan_administrasi.api import router as surat_router
from features.pengaduan_warga.api import router as pengaduan_router
from features.potensi_ekonomi.api import router as ekonomi_router
from features.profil_wilayah.api import router as wilayah_router
from features.publikasi_informasi.api import router as publikasi_router

api = NinjaAPI(
    title="Portal Desa Mandian Gajah API",
    version="1.2.0",
    description="API terintegrasi untuk layanan administrasi dan informasi desa.",
    csrf=not settings.DISABLE_CSRF
)

# Aktifkan penanganan error global dari toolbox
register_exception_handlers(api)

# Daftarkan semua router di sini
api.add_router("/auth", auth_router)
api.add_router("/dashboard-admin", dashboard_router)
api.add_router("/homepage", homepage_router)
api.add_router("/layanan-administrasi", surat_router)
api.add_router("/pengaduan", pengaduan_router)
api.add_router("/potensi-ekonomi", ekonomi_router)
api.add_router("/profil-wilayah", wilayah_router)
api.add_router("/publikasi", publikasi_router)
