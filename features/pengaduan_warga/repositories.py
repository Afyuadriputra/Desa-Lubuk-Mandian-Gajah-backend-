# features/pengaduan_warga/repositories.py

from django.db import transaction
from django.db.models import QuerySet

from features.pengaduan_warga.domain import STATUS_OPEN
from features.pengaduan_warga.models import LayananPengaduan, LayananPengaduanHistory


class PengaduanRepository:
    def get_by_id(self, pengaduan_id) -> LayananPengaduan | None:
        return LayananPengaduan.objects.select_related("pelapor").filter(id=pengaduan_id).first()

    def list_by_pelapor(self, pelapor_id) -> QuerySet[LayananPengaduan]:
        return LayananPengaduan.objects.filter(pelapor_id=pelapor_id)

    def list_all(self) -> QuerySet[LayananPengaduan]:
        return LayananPengaduan.objects.select_related("pelapor").all()

    @transaction.atomic
    def create_pengaduan(self, pelapor_id, kategori: str, judul: str, deskripsi: str, foto_bukti=None) -> LayananPengaduan:
        pengaduan = LayananPengaduan.objects.create(
            pelapor_id=pelapor_id,
            kategori=kategori,
            judul=judul,
            deskripsi=deskripsi,
            foto_bukti=foto_bukti,
            status=STATUS_OPEN
        )
        
        LayananPengaduanHistory.objects.create(
            pengaduan=pengaduan,
            status_from=None,
            status_to=STATUS_OPEN,
            changed_by_id=pelapor_id,
            notes="Pengaduan baru dibuat."
        )
        return pengaduan

    @transaction.atomic
    def update_status(self, pengaduan: LayananPengaduan, new_status: str, actor_id, notes: str | None = None) -> LayananPengaduan:
        old_status = pengaduan.status
        pengaduan.status = new_status
        pengaduan.save(update_fields=["status", "updated_at"])

        LayananPengaduanHistory.objects.create(
            pengaduan=pengaduan,
            status_from=old_status,
            status_to=new_status,
            changed_by_id=actor_id,
            notes=notes
        )
        return pengaduan