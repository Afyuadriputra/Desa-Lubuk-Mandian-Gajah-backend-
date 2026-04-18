# features/pengaduan_warga/services.py

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from features.pengaduan_warga.domain import (
    PengaduanError,
    validate_pengaduan_input,
    validate_resolution_note,
    validate_status_transition,
)
from features.pengaduan_warga.models import LayananPengaduan
from features.pengaduan_warga.permissions import (
    can_submit_pengaduan,
    can_update_pengaduan_status,
    can_view_pengaduan_detail,
)
from features.pengaduan_warga.repositories import PengaduanRepository
from toolbox.logging import audit_event, get_logger
from toolbox.security.permissions import can_view_all_pengaduan
from toolbox.security.upload_validators import validate_image_upload


class PermissionDeniedError(Exception):
    pass

class PengaduanNotFoundError(Exception):
    pass

class FileUploadError(Exception):
    pass


class PengaduanService:
    def __init__(self, repository: PengaduanRepository | None = None):
        self.repository = repository or PengaduanRepository()
        self.logger = get_logger("features.pengaduan_warga.services")

    def buat_pengaduan(self, actor, kategori: str, judul: str, deskripsi: str, foto_bukti=None) -> LayananPengaduan:
        if not can_submit_pengaduan(actor):
            raise PermissionDeniedError("Hanya warga yang dapat membuat pengaduan.")

        validate_pengaduan_input(kategori, judul, deskripsi)

        if foto_bukti:
            try:
                validate_image_upload(foto_bukti)
            except ValidationError as e:
                raise FileUploadError(str(e.message))

        pengaduan = self.repository.create_pengaduan(
            pelapor_id=actor.id,
            kategori=kategori.strip(),
            judul=judul.strip(),
            deskripsi=deskripsi.strip(),
            foto_bukti=foto_bukti
        )

        audit_event(
            action="PENGADUAN_CREATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_pengaduan",
            target_id=pengaduan.id,
            metadata={"kategori": kategori}
        )

        return pengaduan

    def get_pengaduan_detail(self, actor, pengaduan_id) -> LayananPengaduan:
        pengaduan = self.repository.get_detail_by_id(pengaduan_id)
        if not pengaduan:
            raise PengaduanNotFoundError("Data pengaduan tidak ditemukan.")

        if not can_view_pengaduan_detail(actor, pengaduan):
            raise PermissionDeniedError("Anda tidak memiliki akses ke pengaduan ini.")

        return pengaduan

    def list_pengaduan(self, actor) -> QuerySet[LayananPengaduan]:
        if can_view_all_pengaduan(actor):
            return self.repository.list_all()
        return self.repository.list_by_pelapor(actor.id)

    def proses_pengaduan(self, actor, pengaduan_id, new_status: str, notes: str | None = None) -> LayananPengaduan:
        if not can_update_pengaduan_status(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin untuk memproses pengaduan.")

        pengaduan = self.repository.get_by_id(pengaduan_id)
        if not pengaduan:
            raise PengaduanNotFoundError("Data pengaduan tidak ditemukan.")

        previous_status = pengaduan.status
        validate_status_transition(pengaduan.status, new_status)
        validate_resolution_note(new_status, notes)

        updated_pengaduan = self.repository.update_status(
            pengaduan=pengaduan,
            new_status=new_status,
            actor_id=actor.id,
            notes=notes
        )

        audit_event(
            action="PENGADUAN_STATUS_UPDATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_pengaduan",
            target_id=pengaduan.id,
            metadata={"old_status": previous_status, "new_status": new_status}
        )

        return updated_pengaduan
