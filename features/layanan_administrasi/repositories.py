# features/layanan_administrasi/repositories.py

"""
Layer: Repositories

Tanggung jawab:
- Semua akses database untuk fitur layanan administrasi.
- Tidak berisi validasi bisnis.
- Tidak cek permission.
- Tidak generate dokumen.
"""

from django.db import transaction
from django.db.models import QuerySet

from features.layanan_administrasi.domain import (
    STATUS_PENDING,
    STATUS_REJECTED,
    normalize_template_code,
)
from features.layanan_administrasi.models import (
    LayananSurat,
    LayananSuratStatusHistory,
    TemplateSurat,
)


# ============================================================
# Repository Surat
# ============================================================

class SuratRepository:
    def get_by_id(self, surat_id) -> LayananSurat | None:
        return (
            LayananSurat.objects
            .select_related("pemohon", "template")
            .filter(id=surat_id)
            .first()
        )

    def get_detail_by_id(self, surat_id) -> LayananSurat | None:
        return (
            LayananSurat.objects
            .select_related("pemohon", "template")
            .prefetch_related("histori_status__changed_by")
            .filter(id=surat_id)
            .first()
        )

    def list_by_pemohon(self, pemohon_id) -> QuerySet[LayananSurat]:
        return (
            LayananSurat.objects
            .select_related("pemohon", "template")
            .filter(pemohon_id=pemohon_id)
        )

    def list_all(self) -> QuerySet[LayananSurat]:
        return (
            LayananSurat.objects
            .select_related("pemohon", "template")
            .all()
        )

    @transaction.atomic
    def create_surat(
        self,
        pemohon_id,
        keperluan: str,
        jenis_surat: str | None = None,
        template: TemplateSurat | None = None,
    ) -> LayananSurat:
        """
        Membuat pengajuan surat.

        Catatan:
        - Jika template tersedia, jenis_surat diambil dari template.kode.
        - Jika belum pakai template, jenis_surat tetap bisa dikirim manual
          untuk kompatibilitas flow lama.
        """
        final_jenis_surat = template.kode if template else jenis_surat

        surat = LayananSurat.objects.create(
            pemohon_id=pemohon_id,
            template=template,
            jenis_surat=final_jenis_surat,
            keperluan=keperluan,
            status=STATUS_PENDING,
        )

        self.create_status_history(
            surat=surat,
            status_from=None,
            status_to=STATUS_PENDING,
            actor_id=pemohon_id,
            notes="Pengajuan surat baru.",
        )

        return surat

    @transaction.atomic
    def update_status(
        self,
        surat: LayananSurat,
        new_status: str,
        actor_id,
        notes: str | None = None,
        nomor_surat: str | None = None,
        rejection_reason: str | None = None,
    ) -> LayananSurat:
        old_status = surat.status
        surat.status = new_status

        if nomor_surat:
            surat.nomor_surat = nomor_surat

        if new_status == STATUS_REJECTED:
            surat.rejection_reason = rejection_reason

        surat.save()

        self.create_status_history(
            surat=surat,
            status_from=old_status,
            status_to=new_status,
            actor_id=actor_id,
            notes=notes,
        )

        return surat

    def save_generated_docx(self, surat: LayananSurat, filename: str, content_file) -> LayananSurat:
        """
        Menyimpan file DOCX hasil generate ke LayananSurat.

        content_file:
        - Biasanya ContentFile dari django.core.files.base.
        - Repository tidak peduli isi file dibuat dari mana.
        """
        surat.docx_file.save(filename, content_file, save=True)
        return surat

    def save_generated_pdf(self, surat: LayananSurat, filename: str, content_file) -> LayananSurat:
        """
        Menyimpan file PDF hasil generate.

        Tetap dipertahankan untuk kompatibilitas fitur lama.
        """
        surat.pdf_file.save(filename, content_file, save=True)
        return surat

    def create_status_history(
        self,
        surat: LayananSurat,
        status_from: str | None,
        status_to: str,
        actor_id,
        notes: str | None = None,
    ) -> LayananSuratStatusHistory:
        return LayananSuratStatusHistory.objects.create(
            surat=surat,
            status_from=status_from,
            status_to=status_to,
            changed_by_id=actor_id,
            notes=notes,
        )


# ============================================================
# Repository Template Surat
# ============================================================

class TemplateSuratRepository:
    def get_by_id(self, template_id: int) -> TemplateSurat | None:
        return TemplateSurat.objects.filter(id=template_id).first()

    def get_active_by_id(self, template_id: int) -> TemplateSurat | None:
        return TemplateSurat.objects.filter(id=template_id, is_active=True).first()

    def get_by_kode(self, kode: str) -> TemplateSurat | None:
        return TemplateSurat.objects.filter(kode=normalize_template_code(kode)).first()

    def get_active_by_kode(self, kode: str) -> TemplateSurat | None:
        return TemplateSurat.objects.filter(
            kode=normalize_template_code(kode),
            is_active=True,
        ).first()

    def list_all(self) -> QuerySet[TemplateSurat]:
        return TemplateSurat.objects.all()

    def list_active(self) -> QuerySet[TemplateSurat]:
        return TemplateSurat.objects.filter(is_active=True)

    def create_template(
        self,
        kode: str,
        nama: str,
        deskripsi: str | None,
        file_template,
        is_active: bool = True,
    ) -> TemplateSurat:
        return TemplateSurat.objects.create(
            kode=normalize_template_code(kode),
            nama=nama.strip(),
            deskripsi=deskripsi,
            file_template=file_template,
            is_active=is_active,
        )

    def update_template(
        self,
        template: TemplateSurat,
        nama: str | None = None,
        deskripsi: str | None = None,
        file_template=None,
        is_active: bool | None = None,
    ) -> TemplateSurat:
        if nama is not None:
            template.nama = nama.strip()

        if deskripsi is not None:
            template.deskripsi = deskripsi

        if file_template is not None:
            template.file_template = file_template

        if is_active is not None:
            template.is_active = is_active

        template.save()
        return template

    def delete_template(self, template: TemplateSurat) -> None:
        template.delete()