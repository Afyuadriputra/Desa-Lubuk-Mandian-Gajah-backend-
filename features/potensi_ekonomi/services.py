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
)
from features.potensi_ekonomi.repositories import UnitUsahaRepository
from toolbox.logging import audit_event, get_logger
from toolbox.security.upload_validators import validate_image_upload
from toolbox.security.sanitizers import sanitize_html, sanitize_plain_text


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

        normalized_data = self._normalize_input_data(data)
        validate_kategori(normalized_data.get("kategori"))
        validate_input_usaha(normalized_data.get("nama_usaha"), normalized_data.get("kontak_wa", ""))

        if foto:
            try:
                validate_image_upload(foto)
            except ValidationError as e:
                raise FileUploadError(str(e.message))

        create_data = normalized_data
        
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

    def get_katalog_publik(self) -> QuerySet[BumdesUnitUsaha]:
        """Menampilkan data untuk warga (hanya yang is_published=True)."""
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

    def ubah_unit_usaha(self, actor, unit_id: int, data: dict, foto=None) -> BumdesUnitUsaha:
        if not can_manage_data_bumdes(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin mengelola data BUMDes.")

        unit = self.repository.get_by_id(unit_id)
        if not unit:
            raise UnitUsahaNotFoundError("Data unit usaha tidak ditemukan.")

        normalized_data = self._normalize_input_data(data)
        validate_kategori(normalized_data.get("kategori"))
        validate_input_usaha(normalized_data.get("nama_usaha"), normalized_data.get("kontak_wa", ""))

        if foto:
            try:
                validate_image_upload(foto)
            except ValidationError as e:
                raise FileUploadError(str(e.message))
            normalized_data["foto_utama"] = foto

        updated = self.repository.update_unit(unit, normalized_data)
        audit_event(
            action="BUMDES_UNIT_UPDATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="bumdes_unit_usaha",
            target_id=updated.id,
            metadata={"nama_usaha": updated.nama_usaha},
        )
        return updated

    def hapus_unit_usaha(self, actor, unit_id: int) -> None:
        if not can_manage_data_bumdes(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin mengelola data BUMDes.")

        unit = self.repository.get_by_id(unit_id)
        if not unit:
            raise UnitUsahaNotFoundError("Data unit usaha tidak ditemukan.")

        target_id = unit.id
        self.repository.delete_unit(unit)
        audit_event(
            action="BUMDES_UNIT_DELETED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="bumdes_unit_usaha",
            target_id=target_id,
            metadata={},
        )

    def _normalize_input_data(self, data: dict) -> dict:
        return {
            "nama_usaha": sanitize_plain_text(data.get("nama_usaha")),
            "kategori": data.get("kategori"),
            "deskripsi": sanitize_html(data.get("deskripsi")) or "-",
            "fasilitas": sanitize_html(data.get("fasilitas")) if data.get("fasilitas") else None,
            "kontak_wa": data.get("kontak_wa"),
            "harga_tiket": data.get("harga_tiket"),
            "is_published": data.get("is_published", False),
        }
