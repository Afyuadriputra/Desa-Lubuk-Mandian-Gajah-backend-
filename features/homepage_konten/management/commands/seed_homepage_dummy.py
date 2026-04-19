from __future__ import annotations

import base64

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from features.homepage_konten.dummy_data import (
    build_culture_cards,
    build_dummy_dusun_names,
    build_dummy_potentials,
    build_facilities,
    build_footer_links,
    build_gallery_items,
    build_homepage_content_defaults,
    build_potential_opportunities,
    build_recovery_items,
    build_stats_items,
)
from features.homepage_konten.models import (
    HomepageContent,
    HomepageCultureCard,
    HomepageFacility,
    HomepageFooterLink,
    HomepageGalleryItem,
    HomepagePotentialOpportunityItem,
    HomepageRecoveryItem,
    HomepageStatisticItem,
)
from features.potensi_ekonomi.models import BumdesUnitUsaha
from features.profil_wilayah.models import WilayahDusun


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9lJawAAAAASUVORK5CYII="
)


class Command(BaseCommand):
    help = "Isi dummy homepage content agar frontend homepage bisa langsung hidup dari backend."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Hapus child items homepage dan regenerate seluruh dummy content.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options["reset"]
        content = self._seed_homepage_content()

        if reset:
            self._clear_homepage_children(content)

        self._seed_homepage_children(content)
        self._seed_dusun()
        created_potentials = self._seed_potentials()

        self.stdout.write(self.style.SUCCESS("Homepage dummy seed selesai."))
        self.stdout.write(f"- HomepageContent id={content.id}")
        self.stdout.write(f"- Published potentials dibuat/diperbarui: {created_potentials}")

    def _seed_homepage_content(self) -> HomepageContent:
        defaults = build_homepage_content_defaults()
        content, _ = HomepageContent.objects.get_or_create(id=1, defaults=defaults)

        for field, value in defaults.items():
            setattr(content, field, value)
        content.save()
        return content

    def _clear_homepage_children(self, content: HomepageContent) -> None:
        HomepageCultureCard.objects.filter(homepage=content).delete()
        HomepageRecoveryItem.objects.filter(homepage=content).delete()
        HomepagePotentialOpportunityItem.objects.filter(homepage=content).delete()
        HomepageFacility.objects.filter(homepage=content).delete()
        HomepageGalleryItem.objects.filter(homepage=content).delete()
        HomepageFooterLink.objects.filter(homepage=content).delete()
        HomepageStatisticItem.objects.filter(homepage=content).delete()

    def _seed_homepage_children(self, content: HomepageContent) -> None:
        self._replace_children(HomepageCultureCard, content, build_culture_cards())
        self._replace_children(HomepageRecoveryItem, content, build_recovery_items())
        self._replace_children(
            HomepagePotentialOpportunityItem,
            content,
            build_potential_opportunities(),
        )
        self._replace_children(HomepageFacility, content, build_facilities())
        self._replace_children(HomepageGalleryItem, content, build_gallery_items())
        self._replace_children(HomepageFooterLink, content, build_footer_links())
        self._replace_children(HomepageStatisticItem, content, build_stats_items())

    def _replace_children(self, model, content: HomepageContent, items: list[dict]) -> None:
        model.objects.filter(homepage=content).delete()
        model.objects.bulk_create([model(homepage=content, **item) for item in items])

    def _seed_dusun(self) -> None:
        existing_names = set(WilayahDusun.objects.values_list("nama_dusun", flat=True))
        for name in build_dummy_dusun_names():
            if name in existing_names:
                continue
            WilayahDusun.objects.create(nama_dusun=name, kepala_dusun=f"Kepala {name}")

    def _seed_potentials(self) -> int:
        count = 0
        for item in build_dummy_potentials():
            usaha, _ = BumdesUnitUsaha.objects.get_or_create(
                nama_usaha=item.nama_usaha,
                defaults={
                    "kategori": item.kategori,
                    "deskripsi": item.deskripsi,
                    "kontak_wa": item.kontak_wa,
                    "is_published": True,
                },
            )
            usaha.kategori = item.kategori
            usaha.deskripsi = item.deskripsi
            usaha.kontak_wa = item.kontak_wa
            usaha.is_published = True

            if not usaha.foto_utama:
                usaha.foto_utama.save(
                    f"{item.file_stub}.png",
                    ContentFile(ONE_PIXEL_PNG),
                    save=False,
                )

            usaha.save()
            count += 1
        return count
