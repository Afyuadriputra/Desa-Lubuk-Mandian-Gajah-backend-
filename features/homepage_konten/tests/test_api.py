import json
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from django.test import override_settings

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
from features.profil_wilayah.models import ProfilDesa, WilayahDusun


def _homepage_content_payload():
    return {
        "villageName": "Lubuk Mandian Gajah",
        "tagline": "Jejak Sejarah Melayu Petalangan",
        "heroDescription": "Desa dengan sejarah panjang, sungai, dan kawasan gambut yang penting.",
        "heroImage": "https://example.com/hero.jpg",
        "heroBadge": "Desa Peduli Gambut",
        "brand": {
            "logoUrl": "https://example.com/logo.png",
            "logoAlt": "Logo Pelalawan",
            "regionLabel": "Kabupaten Pelalawan",
        },
        "quickStatsDescription": "Desa dengan karakter dataran rendah dan masyarakat yang aktif.",
        "contact": {
            "address": "Jl. Raya Desa No. 1",
            "whatsapp": "+62 812-0000-0000",
            "mapImage": "https://example.com/map.jpg",
        },
        "namingTitle": "Kenapa Mandian Gajah?",
        "namingDescription": "Nama ini berakar dari kisah gajah yang mandi di tepian sungai.",
        "namingImage": "https://example.com/naming.jpg",
        "namingQuote": "Jejak kawanan gajah di tepian sungai.",
        "cultureTitle": "Akar Budaya",
        "cultureDescription": "Budaya Melayu Petalangan masih hidup dalam kehidupan sehari-hari.",
        "sialangTitle": "Kopung Sialang",
        "sialangDescription": "Kawasan adat dengan pohon sialang dan tradisi menumbai.",
        "sialangImage": "https://example.com/sialang.jpg",
        "sialangBadge": "Kearifan Lokal",
        "sialangStat": "50.6 Hektar Area Lindung",
        "sialangQuote": "Menjaga sialang berarti menjaga berkah alam.",
        "peatTitle": "Desa dan Gambut",
        "peatDescription": "Pemulihan ekosistem gambut menjadi bagian dari masa depan desa.",
        "peatQuote": "Gambut adalah sejarah dan masa depan.",
        "peatImages": ["https://example.com/peat-1.jpg", "https://example.com/peat-2.jpg"],
        "recoveryTitle": "Dari Karhutla ke Pemulihan",
        "recoveryDescription": "Desa bergerak dari krisis kebakaran menuju pemulihan bersama yang lebih berkelanjutan.",
        "potentialTitle": "Potensi Unggulan Desa",
        "potentialQuote": "Ekonomi desa tumbuh dari hasil alam dan gotong royong.",
        "potentialOpportunitiesTitle": "Potensi yang Bisa Berkembang",
        "facilitiesTitle": "Fasilitas Desa",
        "galleryTitle": "Galeri Desa",
        "galleryDescription": "Potret visual desa yang memperlihatkan ruang hidup, lanskap, dan aktivitas warga.",
        "contactTitle": "Hubungi Kami",
        "contactDescription": "Kontak dan lokasi desa untuk komunikasi, koordinasi, dan kunjungan lapangan.",
        "footerDescription": "Melestarikan warisan leluhur dan menjaga keseimbangan alam.",
        "footerBadges": ["Wonderful Indonesia", "Riau"],
        "footerCopyright": "© 2026 Desa Lubuk Mandian Gajah.",
        "officeHours": [
            {"day": "Senin - Kamis", "time": "08:00 - 15:00"},
            {"day": "Jumat", "time": "08:00 - 11:30"},
        ],
    }


@pytest.mark.django_db
class TestHomepageKontenAPI:
    def test_named_routes_bisa_di_reverse(self):
        simple_route_names = [
            "homepage-public",
            "homepage-admin-content",
            "homepage-admin-content-update",
            "homepage-admin-culture-create",
            "homepage-admin-recovery-create",
            "homepage-admin-opportunity-create",
            "homepage-admin-facility-create",
            "homepage-admin-gallery-create",
            "homepage-admin-footer-link-create",
            "homepage-admin-stat-create",
        ]
        detail_route_names = [
            "homepage-admin-culture-update",
            "homepage-admin-culture-delete",
            "homepage-admin-recovery-update",
            "homepage-admin-recovery-delete",
            "homepage-admin-opportunity-update",
            "homepage-admin-opportunity-delete",
            "homepage-admin-facility-update",
            "homepage-admin-facility-delete",
            "homepage-admin-gallery-update",
            "homepage-admin-gallery-delete",
            "homepage-admin-footer-link-update",
            "homepage-admin-footer-link-delete",
            "homepage-admin-stat-update",
            "homepage-admin-stat-delete",
        ]

        for name in simple_route_names:
            assert reverse(name)
        for name in detail_route_names:
            assert reverse(name, kwargs={"item_id": 1})

    def test_guest_bisa_akses_homepage_dengan_shape_stabil(self, client):
        response = client.get(reverse("homepage-public"))

        assert response.status_code == 200
        payload = response.json()
        assert payload["villageName"] == "Lubuk Mandian Gajah"
        assert payload["stats"] == [{"value": "0", "label": "Dusun"}]
        assert payload["potentials"] == []
        assert isinstance(payload["cultureCards"], list)
        assert isinstance(payload["officeHours"], list)

    def test_public_homepage_menggabungkan_data_existing_dan_konten(self, client):
        ProfilDesa.objects.create(id=1, visi="Visi", misi="Misi", sejarah="Sejarah desa dari profil.")
        WilayahDusun.objects.create(nama_dusun="Dusun Barat", kepala_dusun="Pak Budi")
        WilayahDusun.objects.create(nama_dusun="Dusun Timur", kepala_dusun="Bu Sari")
        BumdesUnitUsaha.objects.create(
            nama_usaha="Kebun Karet",
            kategori="JASA",
            deskripsi="Potensi ekonomi desa",
            is_published=True,
        )
        BumdesUnitUsaha.objects.create(
            nama_usaha="Draft Internal",
            kategori="JASA",
            deskripsi="Tidak tampil",
            is_published=False,
        )

        content = HomepageContent.objects.create(
            id=1,
            tagline="Tagline publik",
            hero_image="https://example.com/hero.jpg",
            hero_badge="Badge",
            brand_logo_url="https://example.com/logo.png",
            brand_logo_alt="Logo",
            brand_region_label="Pelalawan",
            quick_stats_description="Ringkasan statistik desa.",
            contact_whatsapp="+62 812-0000-0000",
            contact_map_image="https://example.com/map.jpg",
            naming_title="Nama Desa",
            naming_description="Deskripsi penamaan desa yang cukup panjang.",
            naming_image="https://example.com/naming.jpg",
            naming_quote="Kutipan penamaan desa.",
            culture_title="Budaya",
            culture_description="Budaya desa tetap hidup.",
            sialang_title="Sialang",
            sialang_description="Kawasan adat sialang.",
            sialang_image="https://example.com/sialang.jpg",
            sialang_badge="Adat",
            sialang_stat="50 Ha",
            sialang_quote="Menjaga hutan adat.",
            peat_title="Gambut",
            peat_description="Desa dan gambut saling terkait.",
            peat_quote="Gambut adalah masa depan.",
            peat_images=["https://example.com/peat.jpg"],
            recovery_title="Dari Karhutla ke Pemulihan",
            recovery_description="Desa memulihkan lingkungan lewat langkah bertahap.",
            potential_title="Potensi Unggulan Desa",
            potential_quote="Potensi ekonomi tumbuh.",
            potential_opportunities_title="Potensi yang Bisa Berkembang",
            facilities_title="Fasilitas",
            gallery_title="Galeri Desa",
            gallery_description="Dokumentasi visual ruang dan kehidupan desa.",
            contact_title="Hubungi Kami",
            contact_description="Kontak desa untuk koordinasi dan kunjungan.",
            footer_description="Footer desa.",
            footer_badges=["Badge A"],
            footer_copyright="© Desa",
            office_hours=[{"day": "Senin", "time": "08:00 - 15:00", "danger": False}],
        )
        HomepageCultureCard.objects.create(
            homepage=content,
            icon="groups",
            title="Kartu 2",
            description="Urutan kedua",
            sort_order=2,
        )
        HomepageCultureCard.objects.create(
            homepage=content,
            icon="history",
            title="Kartu 1",
            description="Urutan pertama",
            sort_order=1,
        )
        HomepageStatisticItem.objects.create(
            homepage=content,
            label="RW",
            value="4",
            sort_order=1,
        )
        HomepageStatisticItem.objects.create(
            homepage=content,
            label="RT",
            value="8",
            sort_order=2,
        )

        response = client.get(reverse("homepage-public"))

        assert response.status_code == 200
        payload = response.json()
        assert payload["heroDescription"] == "Sejarah desa dari profil."
        assert payload["stats"] == [
            {"value": "2", "label": "Dusun"},
            {"value": "4", "label": "RW"},
            {"value": "8", "label": "RT"},
        ]
        assert payload["potentials"] == [{"title": "Kebun Karet", "image": ""}]
        assert [item["title"] for item in payload["cultureCards"]] == ["Kartu 1", "Kartu 2"]

    @override_settings(
        BACKEND_PUBLIC_BASE_URL="http://127.0.0.1:8000",
        MEDIA_ROOT=Path(__file__).resolve().parent / "test_media",
    )
    def test_public_homepage_mengembalikan_absolute_media_url_untuk_potentials(
        self, client
    ):
        image_file = SimpleUploadedFile(
            "potensi.png",
            (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc\xf8"
                b"\xff\xff?\x00\x05\xfe\x02\xfeA\xd9\x8f\x88\x00\x00\x00\x00IEND\xaeB`\x82"
            ),
            content_type="image/png",
        )
        BumdesUnitUsaha.objects.create(
            nama_usaha="Madu Hutan",
            kategori="JASA",
            deskripsi="Potensi desa",
            is_published=True,
            foto_utama=image_file,
        )

        response = client.get(reverse("homepage-public"))

        assert response.status_code == 200
        payload = response.json()
        assert payload["potentials"][0]["title"] == "Madu Hutan"
        assert payload["potentials"][0]["image"].startswith("http://127.0.0.1:8000/media/bumdes/")

    def test_admin_bisa_update_content_dan_input_disanitasi(self, client, admin_user):
        client.force_login(admin_user)
        payload = _homepage_content_payload()
        payload["tagline"] = "<script>alert(1)</script>Tagline Aman"

        response = client.put(
            reverse("homepage-admin-content-update"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert "<script>" not in data["tagline"]
        content = HomepageContent.objects.get(id=1)
        assert content.tagline == "Tagline Aman"

    def test_warga_ditolak_ke_endpoint_admin(self, client, warga_user):
        client.force_login(warga_user)

        response = client.get(reverse("homepage-admin-content"))

        assert response.status_code in {401, 403}

    def test_admin_bisa_crud_child_sections(self, client, admin_user):
        client.force_login(admin_user)
        HomepageContent.objects.get_or_create(id=1)

        create_payload = {
            "icon": "groups",
            "title": "Budaya Melayu",
            "description": "Tradisi lokal tetap hidup dan dijaga.",
            "sort_order": 1,
        }
        create_response = client.post(
            reverse("homepage-admin-culture-create"),
            data=json.dumps(create_payload),
            content_type="application/json",
        )
        assert create_response.status_code == 201

        item_id = create_response.json()["data"]["id"]

        update_payload = {
            "icon": "groups",
            "title": "Budaya Melayu Baru",
            "description": "Tradisi lokal tetap hidup dan makin diperkuat.",
            "sort_order": 0,
        }
        update_response = client.put(
            reverse("homepage-admin-culture-update", kwargs={"item_id": item_id}),
            data=json.dumps(update_payload),
            content_type="application/json",
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["title"] == "Budaya Melayu Baru"

        delete_response = client.delete(reverse("homepage-admin-culture-delete", kwargs={"item_id": item_id}))
        assert delete_response.status_code == 200
        assert HomepageCultureCard.objects.filter(id=item_id).exists() is False

    def test_admin_bisa_crud_stat_items(self, client, admin_user):
        client.force_login(admin_user)
        HomepageContent.objects.get_or_create(id=1)

        create_response = client.post(
            reverse("homepage-admin-stat-create"),
            data=json.dumps({"label": "Jiwa", "value": "791", "sort_order": 1}),
            content_type="application/json",
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["data"]["id"]

        update_response = client.put(
            reverse("homepage-admin-stat-update", kwargs={"item_id": item_id}),
            data=json.dumps({"label": "KK", "value": "233", "sort_order": 2}),
            content_type="application/json",
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["label"] == "KK"

        delete_response = client.delete(reverse("homepage-admin-stat-delete", kwargs={"item_id": item_id}))
        assert delete_response.status_code == 200
        assert HomepageStatisticItem.objects.filter(id=item_id).exists() is False

    def test_admin_content_memuat_semua_child_items(self, client, admin_user):
        client.force_login(admin_user)
        content = HomepageContent.objects.create(
            id=1,
            village_name="Desa Test",
            tagline="Tagline",
            hero_description="Hero description yang cukup panjang.",
            hero_image="https://example.com/hero.jpg",
            hero_badge="Badge",
            brand_logo_url="https://example.com/logo.png",
            brand_logo_alt="Logo",
            brand_region_label="Pelalawan",
            contact_address="Alamat Desa",
            contact_whatsapp="+62 812-0000-0000",
            contact_map_image="https://example.com/map.jpg",
            quick_stats_description="Deskripsi statistik.",
            naming_title="Nama",
            naming_description="Deskripsi nama desa.",
            naming_image="https://example.com/naming.jpg",
            naming_quote="Quote",
            culture_title="Budaya",
            culture_description="Deskripsi budaya.",
            sialang_title="Sialang",
            sialang_description="Deskripsi sialang.",
            sialang_image="https://example.com/sialang.jpg",
            sialang_badge="Badge",
            sialang_stat="50 Ha",
            sialang_quote="Quote sialang",
            peat_title="Gambut",
            peat_description="Deskripsi gambut.",
            peat_quote="Quote gambut",
            potential_quote="Quote potensi",
            facilities_title="Fasilitas",
            footer_description="Deskripsi footer.",
            footer_badges=["A"],
            footer_copyright="© Test",
            office_hours=[{"day": "Senin", "time": "08:00 - 15:00", "danger": False}],
        )
        HomepageRecoveryItem.objects.create(
            homepage=content,
            icon="nature",
            title="Recovery",
            description="Deskripsi recovery item.",
            wrapper="bg-primary",
            sort_order=1,
        )
        HomepagePotentialOpportunityItem.objects.create(
            homepage=content,
            icon="storefront",
            title="Peluang",
            description="Deskripsi peluang ekonomi.",
            sort_order=1,
        )
        HomepageFacility.objects.create(
            homepage=content,
            icon="school",
            label="PAUD",
            sort_order=1,
        )
        HomepageGalleryItem.objects.create(
            homepage=content,
            image="https://example.com/gallery.jpg",
            alt="Galeri",
            tall=True,
            caption="Galeri utama",
            sort_order=1,
        )
        HomepageFooterLink.objects.create(
            homepage=content,
            label="Sejarah",
            href="/sejarah",
            sort_order=1,
        )

        response = client.get(reverse("homepage-admin-content"))

        assert response.status_code == 200
        payload = response.json()["data"]
        assert payload["contactAddressSource"] == "homepage_konten"
        assert payload["villageNameSource"] == "homepage_konten"
        assert len(payload["recoveryItems"]) == 1
        assert len(payload["potentialOpportunityItems"]) == 1
        assert len(payload["facilities"]) == 1
        assert len(payload["gallery"]) == 1
        assert len(payload["footerLinks"]) == 1


@pytest.mark.django_db
@override_settings(
    BACKEND_PUBLIC_BASE_URL="http://127.0.0.1:8000",
    MEDIA_ROOT=Path(__file__).resolve().parent / "test_media_seed",
)
def test_command_seed_homepage_dummy_mengisi_data_dan_relasi():
    call_command("seed_homepage_dummy", "--reset")

    content = HomepageContent.objects.get(id=1)
    assert content.village_name == "Desa Segamai"
    assert content.tagline
    assert HomepageCultureCard.objects.filter(homepage=content).count() >= 3
    assert HomepageRecoveryItem.objects.filter(homepage=content).count() >= 3
    assert HomepagePotentialOpportunityItem.objects.filter(homepage=content).count() >= 3
    assert HomepageFacility.objects.filter(homepage=content).count() >= 4
    assert HomepageGalleryItem.objects.filter(homepage=content).count() >= 4
    assert HomepageFooterLink.objects.filter(homepage=content).count() >= 4
    assert HomepageStatisticItem.objects.filter(homepage=content).count() >= 6
    assert WilayahDusun.objects.count() >= 4
    assert BumdesUnitUsaha.objects.filter(is_published=True).count() >= 5
    assert BumdesUnitUsaha.objects.filter(foto_utama__isnull=False).count() >= 5
