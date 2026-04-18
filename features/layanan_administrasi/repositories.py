# features/layanan_administrasi/repositories.py

from django.db import transaction
from django.db.models import QuerySet

from features.layanan_administrasi.models import LayananSurat, LayananSuratStatusHistory


class SuratRepository:
    def get_by_id(self, surat_id) -> LayananSurat | None:
        return LayananSurat.objects.select_related("pemohon").filter(id=surat_id).first()

    def get_detail_by_id(self, surat_id) -> LayananSurat | None:
        return (
            LayananSurat.objects.select_related("pemohon")
            .prefetch_related("histori_status__changed_by")
            .filter(id=surat_id)
            .first()
        )

    def list_by_pemohon(self, pemohon_id) -> QuerySet[LayananSurat]:
        return LayananSurat.objects.select_related("pemohon").filter(pemohon_id=pemohon_id)

    def list_all(self) -> QuerySet[LayananSurat]:
        return LayananSurat.objects.select_related("pemohon").all()

    @transaction.atomic
    def create_surat(self, pemohon_id, jenis_surat: str, keperluan: str) -> LayananSurat:
        surat = LayananSurat.objects.create(
            pemohon_id=pemohon_id,
            jenis_surat=jenis_surat,
            keperluan=keperluan,
            status="PENDING"
        )
        
        # Rekam histori awal
        LayananSuratStatusHistory.objects.create(
            surat=surat,
            status_from=None,
            status_to="PENDING",
            changed_by_id=pemohon_id,
            notes="Pengajuan surat baru."
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
        rejection_reason: str | None = None
    ) -> LayananSurat:
        old_status = surat.status
        surat.status = new_status
        
        if nomor_surat:
            surat.nomor_surat = nomor_surat
        if rejection_reason and new_status == "REJECTED":
            surat.rejection_reason = rejection_reason
            
        surat.save()

        LayananSuratStatusHistory.objects.create(
            surat=surat,
            status_from=old_status,
            status_to=new_status,
            changed_by_id=actor_id,
            notes=notes
        )
        return surat
