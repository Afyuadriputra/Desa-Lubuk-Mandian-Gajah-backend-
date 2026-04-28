# features/layanan_administrasi/services.py

"""
Layer: Services

Tanggung jawab:
- Mengatur alur bisnis/use case.
- Cek permission.
- Panggil validasi domain.
- Panggil repository.
- Tidak menyimpan query database langsung.
"""

import os
import tempfile

from django.core.files.base import ContentFile
from django.http import FileResponse
from django.db.models import QuerySet
from django.utils import timezone
from docxtpl import DocxTemplate

from features.layanan_administrasi.domain import (
    STATUS_DONE,
    validate_jenis_surat,
    validate_keperluan,
    validate_rejection,
    validate_status_transition,
    validate_template_code,
    validate_template_file,
    validate_template_is_active,
    validate_template_name,
)
from features.layanan_administrasi.models import LayananSurat, TemplateSurat
from features.layanan_administrasi.permissions import (
    can_manage_template_surat,
    can_submit_surat,
    can_update_surat_status,
    can_view_surat_detail,
)
from features.layanan_administrasi.repositories import (
    SuratRepository,
    TemplateSuratRepository,
)
from toolbox.logging import audit_event, get_logger
from toolbox.pdf_generator import generate_nomor_surat
from toolbox.security.permissions import can_view_all_surat


# ============================================================
# Exceptions
# ============================================================

class PermissionDeniedError(Exception):
    pass


class LayananSuratNotFoundError(Exception):
    pass


class TemplateSuratNotFoundError(Exception):
    pass


# ============================================================
# Renderer DOCX
# ============================================================

class SuratDocumentRenderer:
    """Mengisi placeholder pada file .docx dan menghasilkan bytes."""

    def render_docx(self, template_path: str, context: dict) -> bytes:
        doc = DocxTemplate(template_path)
        doc.render(context)

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            doc.save(temp_path)
            with open(temp_path, "rb") as file:
                return file.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


# ============================================================
# Template Surat Service
# ============================================================

class TemplateSuratService:
    """Use case untuk mengelola template surat."""

    def __init__(self, repository: TemplateSuratRepository | None = None):
        self.repository = repository or TemplateSuratRepository()
        self.logger = get_logger("features.layanan_administrasi.template_service")

    def create_template(
        self,
        actor,
        kode: str,
        nama: str,
        deskripsi: str | None,
        file_template,
        is_active: bool = True,
    ) -> TemplateSurat:
        if not can_manage_template_surat(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin mengelola template surat.")

        validate_template_code(kode)
        validate_template_name(nama)
        validate_template_file(file_template.name)

        template = self.repository.create_template(
            kode=kode,
            nama=nama,
            deskripsi=deskripsi,
            file_template=file_template,
            is_active=is_active,
        )

        audit_event(
            action="TEMPLATE_SURAT_CREATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="template_surat",
            target_id=template.id,
            metadata={"kode": template.kode},
        )

        self.logger.info("Template surat berhasil dibuat. ID={id}", id=template.id)
        return template

    def list_active_templates(self) -> QuerySet[TemplateSurat]:
        return self.repository.list_active()

    def list_all_templates(self, actor) -> QuerySet[TemplateSurat]:
        if not can_manage_template_surat(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin melihat semua template surat.")
        return self.repository.list_all()


# ============================================================
# Surat Service
# ============================================================

class SuratService:
    """Use case untuk pengajuan, proses, detail, list, dan download surat."""

    def __init__(
        self,
        repository: SuratRepository | None = None,
        template_repository: TemplateSuratRepository | None = None,
        document_renderer: SuratDocumentRenderer | None = None,
    ):
        self.repository = repository or SuratRepository()
        self.template_repository = template_repository or TemplateSuratRepository()
        self.document_renderer = document_renderer or SuratDocumentRenderer()
        self.logger = get_logger("features.layanan_administrasi.services")

    def ajukan_surat(
        self,
        actor,
        keperluan: str,
        template_id: int | None = None,
        jenis_surat: str | None = None,
    ) -> LayananSurat:
        if not can_submit_surat(actor):
            raise PermissionDeniedError("Hanya warga yang dapat mengajukan surat.")

        validate_keperluan(keperluan)

        template = self._get_active_template_or_none(template_id)

        if not template:
            if not jenis_surat:
                raise TemplateSuratNotFoundError("Template surat wajib dipilih.")
            validate_jenis_surat(jenis_surat)

        surat = self.repository.create_surat(
            pemohon_id=actor.id,
            template=template,
            jenis_surat=jenis_surat,
            keperluan=keperluan.strip(),
        )

        audit_event(
            action="SURAT_SUBMITTED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_surat",
            target_id=surat.id,
            metadata={
                "jenis_surat": surat.jenis_surat,
                "template_id": template.id if template else None,
            },
        )

        self.logger.info("Pengajuan surat berhasil dibuat. ID={id}", id=surat.id)
        return surat

    def list_surat(self, actor) -> QuerySet[LayananSurat]:
        if can_view_all_surat(actor):
            return self.repository.list_all()
        return self.repository.list_by_pemohon(actor.id)

    def get_surat_detail(self, actor, surat_id) -> LayananSurat:
        surat = self.repository.get_detail_by_id(surat_id)
        if not surat:
            raise LayananSuratNotFoundError("Data surat tidak ditemukan.")

        if not can_view_surat_detail(actor, surat):
            raise PermissionDeniedError("Anda tidak memiliki akses untuk melihat surat ini.")

        return surat

    def proses_surat(
        self,
        actor,
        surat_id,
        new_status: str,
        notes: str | None = None,
        nomor_surat: str | None = None,
        rejection_reason: str | None = None,
    ) -> LayananSurat:
        if not can_update_surat_status(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin memproses surat.")

        surat = self.repository.get_detail_by_id(surat_id)
        if not surat:
            raise LayananSuratNotFoundError("Data surat tidak ditemukan.")

        previous_status = surat.status
        validate_status_transition(previous_status, new_status)
        validate_rejection(new_status, rejection_reason)

        final_nomor_surat = self._resolve_nomor_surat(surat, new_status, nomor_surat)

        updated_surat = self.repository.update_status(
            surat=surat,
            new_status=new_status,
            actor_id=actor.id,
            notes=notes,
            nomor_surat=final_nomor_surat,
            rejection_reason=rejection_reason,
        )

        if new_status == STATUS_DONE:
            self._generate_docx_if_template_exists(updated_surat, final_nomor_surat)

        audit_event(
            action="SURAT_STATUS_UPDATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_surat",
            target_id=surat.id,
            metadata={
                "old_status": previous_status,
                "new_status": new_status,
                "docx_generated": bool(updated_surat.docx_file),
            },
        )

        return self.repository.get_detail_by_id(surat.id) or updated_surat

    def download_hasil_surat(self, actor, surat_id):
        surat = self.get_surat_detail(actor, surat_id)

        if surat.status != STATUS_DONE:
            raise PermissionDeniedError("Surat belum selesai diproses.")

        if surat.docx_file:
            return self._file_response(surat.docx_file)

        if surat.pdf_file:
            return self._file_response(surat.pdf_file)

        raise PermissionDeniedError("File hasil surat belum tersedia.")

    def download_pdf(self, actor, surat_id):
        """
        Alias kompatibilitas untuk endpoint lama.
        Sekarang mengarah ke hasil surat utama.
        """
        return self.download_hasil_surat(actor, surat_id)

    # ========================================================
    # Private Helpers
    # ========================================================

    def _get_active_template_or_none(self, template_id: int | None) -> TemplateSurat | None:
        if not template_id:
            return None

        template = self.template_repository.get_active_by_id(template_id)
        validate_template_is_active(template)
        return template

    def _resolve_nomor_surat(
        self,
        surat: LayananSurat,
        new_status: str,
        nomor_surat: str | None,
    ) -> str | None:
        final_nomor = nomor_surat or surat.nomor_surat

        if new_status == STATUS_DONE and not final_nomor:
            return generate_nomor_surat(surat.jenis_surat, str(surat.id))

        return final_nomor

    def _generate_docx_if_template_exists(
        self,
        surat: LayananSurat,
        nomor_surat: str | None,
    ) -> None:
        if not surat.template or not surat.template.file_template:
            self.logger.warning("Surat ID={id} tidak memiliki template DOCX.", id=surat.id)
            return

        try:
            context = self._build_template_context(surat, nomor_surat)
            docx_bytes = self.document_renderer.render_docx(
                surat.template.file_template.path,
                context,
            )

            filename = f"Surat_{surat.jenis_surat}_{surat.pemohon.nik}.docx"
            self.repository.save_generated_docx(
                surat=surat,
                filename=filename,
                content_file=ContentFile(docx_bytes),
            )

            self.logger.info("DOCX surat berhasil dibuat. ID={id}", id=surat.id)

        except Exception as exc:
            self.logger.error(
                "Gagal generate DOCX surat ID={id}: {error}",
                id=surat.id,
                error=str(exc),
            )

    def _build_template_context(self, surat: LayananSurat, nomor_surat: str | None) -> dict:
        return {
            "surat": surat,
            "pemohon": surat.pemohon,
            "nomor_surat": nomor_surat or surat.nomor_surat,
            "tanggal_cetak": timezone.now().strftime("%d-%m-%Y"),
            "nama_kepala_desa": "Bapak Kepala Desa",
        }

    def _file_response(self, file_field):
        return FileResponse(
            file_field.open("rb"),
            as_attachment=True,
            filename=file_field.name.rsplit("/", 1)[-1],
        )