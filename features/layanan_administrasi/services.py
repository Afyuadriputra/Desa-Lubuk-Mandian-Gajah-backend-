# features/layanan_administrasi/services.py

from django.core.files.base import ContentFile
from django.http import FileResponse
from django.db.models import QuerySet
from django.utils import timezone

from features.layanan_administrasi.domain import (
    STATUS_DONE,
    STATUS_REJECTED,
    validate_jenis_surat,
    validate_keperluan,
    validate_rejection,
    validate_status_transition,
)
from features.layanan_administrasi.models import LayananSurat
from features.layanan_administrasi.permissions import (
    can_submit_surat,
    can_update_surat_status,
    can_view_surat_detail,
)
from features.layanan_administrasi.repositories import SuratRepository
from toolbox.logging import audit_event, get_logger
from toolbox.security.permissions import can_view_all_surat

# Import dari toolbox PDF generator yang sudah Anda buat
from toolbox.pdf_generator import (
    generate_nomor_surat,
    generate_pdf_from_html,
    render_surat_html,
)


class PermissionDeniedError(Exception):
    pass


class LayananSuratNotFoundError(Exception):
    pass


class SuratService:
    def __init__(self, repository: SuratRepository | None = None):
        self.repository = repository or SuratRepository()
        self.logger = get_logger("features.layanan_administrasi.services")

    def ajukan_surat(self, actor, jenis_surat: str, keperluan: str) -> LayananSurat:
        if not can_submit_surat(actor):
            raise PermissionDeniedError("Hanya warga yang dapat mengajukan surat.")

        validate_jenis_surat(jenis_surat)
        validate_keperluan(keperluan)

        surat = self.repository.create_surat(
            pemohon_id=actor.id,
            jenis_surat=jenis_surat,
            keperluan=keperluan.strip()
        )

        audit_event(
            action="SURAT_SUBMITTED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_surat",
            target_id=surat.id,
            metadata={"jenis_surat": jenis_surat}
        )

        self.logger.info("Pengajuan surat berhasil dibuat. ID={surat_id}", surat_id=surat.id)
        return surat

    def get_surat_detail(self, actor, surat_id) -> LayananSurat:
        surat = self.repository.get_detail_by_id(surat_id)
        if not surat:
            raise LayananSuratNotFoundError("Data surat tidak ditemukan.")

        if not can_view_surat_detail(actor, surat):
            raise PermissionDeniedError("Anda tidak memiliki akses untuk melihat surat ini.")

        return surat

    def download_pdf(self, actor, surat_id):
        surat = self.get_surat_detail(actor, surat_id)
        if surat.status != STATUS_DONE or not surat.pdf_file:
            raise PermissionDeniedError("PDF surat belum tersedia.")
        return FileResponse(surat.pdf_file.open("rb"), as_attachment=True, filename=surat.pdf_file.name.rsplit("/", 1)[-1])

    def list_surat(self, actor) -> QuerySet[LayananSurat]:
        if can_view_all_surat(actor):
            return self.repository.list_all()
        return self.repository.list_by_pemohon(actor.id)

    def proses_surat(
        self, 
        actor, 
        surat_id, 
        new_status: str, 
        notes: str | None = None,
        nomor_surat: str | None = None,
        rejection_reason: str | None = None
    ) -> LayananSurat:
        if not can_update_surat_status(actor):
            raise PermissionDeniedError("Anda tidak memiliki izin memproses surat.")

        surat = self.repository.get_detail_by_id(surat_id)
        if not surat:
            raise LayananSuratNotFoundError("Data surat tidak ditemukan.")

        previous_status = surat.status

        # Validasi domain rules
        validate_status_transition(previous_status, new_status)
        validate_rejection(new_status, rejection_reason)

        # OTOMATISASI NOMOR SURAT
        final_nomor_surat = nomor_surat or surat.nomor_surat
        if new_status == STATUS_DONE and not final_nomor_surat:
            final_nomor_surat = generate_nomor_surat(surat.jenis_surat, str(surat.id))

        updated_surat = self.repository.update_status(
            surat=surat,
            new_status=new_status,
            actor_id=actor.id,
            notes=notes,
            nomor_surat=final_nomor_surat,
            rejection_reason=rejection_reason
        )

        # GENERATE PDF JIKA STATUS DONE
        if new_status == STATUS_DONE:
            try:
                self.logger.info("Memulai proses generate PDF untuk surat ID={id}", id=surat.id)
                
                context = {
                    "surat": updated_surat,
                    "pemohon": updated_surat.pemohon,
                    "tanggal_cetak": timezone.now(),
                    "nama_kepala_desa": "Bapak Kepala Desa", 
                }
                
                template_name = f"pdf_templates/surat_{updated_surat.jenis_surat.lower()}.html"
                html_string = render_surat_html(template_name, context)
                pdf_bytes = generate_pdf_from_html(html_string)
                
                pdf_filename = f"Surat_{updated_surat.jenis_surat}_{updated_surat.pemohon.nik}.pdf"
                updated_surat.pdf_file.save(pdf_filename, ContentFile(pdf_bytes), save=True)
                
                self.logger.info("Berhasil men-generate dan menyimpan PDF surat ID={id}", id=surat.id)

            except Exception as e:
                self.logger.error("Gagal men-generate PDF untuk surat ID={id}: {error}", id=surat.id, error=str(e))

        audit_event(
            action="SURAT_STATUS_UPDATED",
            actor_id=actor.id,
            actor_role=actor.role,
            target="layanan_surat",
            target_id=surat.id,
            metadata={"old_status": previous_status, "new_status": new_status, "pdf_generated": new_status == STATUS_DONE}
        )

        return self.repository.get_detail_by_id(surat.id) or updated_surat
