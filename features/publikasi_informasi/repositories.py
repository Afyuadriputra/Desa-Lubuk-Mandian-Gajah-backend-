# features/publikasi_informasi/repositories.py

from django.db.models import QuerySet
from features.publikasi_informasi.models import Publikasi
from features.publikasi_informasi.domain import STATUS_PUBLISHED

class PublikasiRepository:
    def get_by_slug(self, slug: str) -> Publikasi | None:
        return Publikasi.objects.select_related("penulis").filter(slug=slug).first()

    def list_published(self, jenis: str | None = None) -> QuerySet[Publikasi]:
        qs = Publikasi.objects.select_related("penulis").filter(status=STATUS_PUBLISHED)
        if jenis:
            qs = qs.filter(jenis=jenis)
        return qs

    def list_all_admin(self) -> QuerySet[Publikasi]:
        return Publikasi.objects.select_related("penulis").all()

    def create(self, data: dict) -> Publikasi:
        return Publikasi.objects.create(**data)

    def update_status(self, publikasi: Publikasi, status: str, published_at) -> Publikasi:
        publikasi.status = status
        publikasi.published_at = published_at
        publikasi.save(update_fields=["status", "published_at", "updated_at"])
        return publikasi