# features/potensi_ekonomi/services.py

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from features.potensi_ekonomi.domain import (
    PotensiEkonomiError,
    validate_input_usaha,
    validate_kategori,
)
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.potensi_ekonomi.permissions import (
    can_manage_data_bumdes,
    can_view_katalog_publik,
)
from features.potensi_ekonomi.repositories import UnitUsahaRepository
from toolbox.logging import audit_event, get_logger
from toolbox.security.upload_validators import validate_image_upload
# Import sanitize_rich_text_content dihapus karena sudah ditangani otomatis oleh Schema Ninja.


class PermissionDeniedError(Exception):
    pass

class UnitUsahaNotFoundError(Exception):
    pass

class FileUploadError(Exception):
    pass


class PotensiEkonomiService:
    def __init__(self, repository: UnitUsahaRepository | None = None):
        self.repository = repository or UnitUsahaRepository()
        self.logger = get_logger("features.potensi_ekonomi.services")

    def buat_unit_usaha(self, actor, data: dict, foto=None) -> BumdesUnitUsaha:
        if not can_manage_data_bumdes(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin mengelola data BUMDes.")

        # Validasi domain (business rules) tetap berjalan
        validate_kategori(data.get("kategori"))
        validate_input_usaha(data.get("nama_usaha"), data.get("kontak_wa", ""))

        if foto:
            try:
                validate_image_upload(foto)
            except ValidationError as e:
                raise FileUploadError(str(e.message))

        # KISS & DRY: Dictionary 'data' dari API Pydantic/Ninja sudah terjamin 
        # tipe datanya (boolean, float) dan bersih dari XSS (SafeHTMLString).
        create_data = {
            "nama_usaha": data.get("nama_usaha"),
            "kategori": data.get("kategori"),
            "deskripsi": data.get("deskripsi"),
            "fasilitas": data.get("fasilitas"),
            "kontak_wa": data.get("kontak_wa"),
            "harga_tiket": data.get("harga_tiket"),
            "is_published": data.get("is_published", False),
        }
        
        if foto:
            create_data["foto_utama"] = foto

        unit = self.repository.create_unit(create_data)

        audit_event(
            action="BUMDES_UNIT_CREATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="bumdes_unit_usaha",
            target_id=unit.id,
            metadata={"nama_usaha": unit.nama_usaha}
        )

        return unit

    def get_katalog_publik(self, actor) -> QuerySet[BumdesUnitUsaha]:
        """Menampilkan data untuk warga (hanya yang is_published=True)."""
        if not can_view_katalog_publik(actor):
            raise PermissionDeniedError("Akses ditolak.")
        return self.repository.list_published()

    def get_semua_unit_admin(self, actor) -> QuerySet[BumdesUnitUsaha]:
        """Menampilkan semua data untuk admin (termasuk draft)."""
        if not can_manage_data_bumdes(actor):
            raise PermissionDeniedError("Akses ditolak.")
        return self.repository.list_all()

    def get_detail_unit(self, actor, unit_id: int) -> BumdesUnitUsaha:
        unit = self.repository.get_by_id(unit_id)
        if not unit:
            raise UnitUsahaNotFoundError("Data unit usaha tidak ditemukan.")

        # Warga biasa tidak boleh melihat data yang belum dipublish
        if not can_manage_data_bumdes(actor) and not unit.is_published:
             raise PermissionDeniedError("Data ini belum tersedia untuk publik.")

        return unit