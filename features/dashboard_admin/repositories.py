# features/dashboard_admin/repositories.py

from django.db.models import Count
from django.contrib.auth import get_user_model

from features.layanan_administrasi.models import LayananSurat
from features.pengaduan_warga.models import LayananPengaduan
from features.potensi_ekonomi.models import BumdesUnitUsaha

User = get_user_model()

class DashboardRepository:
    def get_summary_metrics(self) -> dict:
        return {
            "total_warga_aktif": User.objects.filter(role="WARGA", is_active=True).count(),
            "surat_pending": LayananSurat.objects.filter(status="PENDING").count(),
            "pengaduan_aktif": LayananPengaduan.objects.filter(status__in=["OPEN", "TRIAGED", "IN_PROGRESS"]).count(),
            "bumdes_published": BumdesUnitUsaha.objects.filter(is_published=True).count()
        }

    def get_surat_stats_by_status(self) -> list:
        # Menghasilkan: [{'status': 'PENDING', 'total': 10}, {'status': 'DONE', 'total': 45}]
        return list(LayananSurat.objects.values('status').annotate(total=Count('id')).order_by('-total'))

    def get_pengaduan_stats_by_kategori(self) -> list:
        # Menghasilkan: [{'kategori': 'Infrastruktur', 'total': 20}, ...]
        return list(LayananPengaduan.objects.values('kategori').annotate(total=Count('id')).order_by('-total'))