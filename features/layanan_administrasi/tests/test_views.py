import json
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
import uuid


from features.layanan_administrasi.domain import JENIS_SKU

User = get_user_model()


# =========================
# BASE FACTORY
# =========================
@pytest.fixture
def user_factory():
    counter = 1

    def create(role="WARGA", is_staff=False):
        nonlocal counter

        nik = str(counter).zfill(16)
        counter += 1

        return User.objects.create_user(
            nik=nik,
            password="pass",
            nama_lengkap=f"User {nik}",
            role=role,
            is_staff=is_staff,
        )

    return create


# =========================
# AJUKAN SURAT
# =========================
@pytest.mark.django_db
class TestAjukanSuratView:

    def test_should_return_401_when_not_authenticated(self):
        client = Client()

        response = client.post(reverse("surat-ajukan"))

        assert response.status_code == 401

    def test_should_allow_warga_submit(self, user_factory):
        client = Client()
        warga = user_factory(role="WARGA")

        client.force_login(warga)

        response = client.post(
            reverse("surat-ajukan"),
            data=json.dumps({
                "jenis_surat": JENIS_SKU,
                "keperluan": "Keperluan panjang sekali"
            }),
            content_type="application/json",
        )

        assert response.status_code == 201

    def test_admin_cannot_submit_surat(self, user_factory):
        client = Client()
        admin = user_factory(role="ADMIN", is_staff=True)

        client.force_login(admin)

        response = client.post(
            reverse("surat-ajukan"),
            data=json.dumps({
                "jenis_surat": JENIS_SKU,
                "keperluan": "Test"
            }),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_invalid_payload_should_fail(self, user_factory):
        client = Client()
        warga = user_factory(role="WARGA")

        client.force_login(warga)

        response = client.post(
            reverse("surat-ajukan"),
            data=json.dumps({
                "jenis_surat": "",  # invalid
                "keperluan": ""
            }),
            content_type="application/json",
        )

        assert response.status_code == 400


# =========================
# LIST SURAT
# =========================
@pytest.mark.django_db
class TestListSuratView:

    def test_should_return_401_when_not_authenticated(self):
        client = Client()

        response = client.get(reverse("surat-list"))

        assert response.status_code == 401


# =========================
# DETAIL SURAT
# =========================
@pytest.mark.django_db
class TestDetailSuratView:

    def test_warga_cannot_view_other_user_surat(self, user_factory):
        client = Client()

        warga1 = user_factory(role="WARGA")
        warga2 = user_factory(role="WARGA")

        from features.layanan_administrasi.services import SuratService
        service = SuratService()

        surat = service.repository.create_surat(
            warga1.id, JENIS_SKU, "Keperluan panjang"
        )

        client.force_login(warga2)

        response = client.get(
            reverse("surat-detail", kwargs={"surat_id": str(surat.id)})
        )

        assert response.status_code == 403


# =========================
# LIST ADVANCED
# =========================
@pytest.mark.django_db
class TestListSuratAdvanced:

    def test_warga_only_see_own_surat(self, user_factory):
        client = Client()

        warga1 = user_factory(role="WARGA")
        warga2 = user_factory(role="WARGA")

        from features.layanan_administrasi.services import SuratService
        service = SuratService()

        service.repository.create_surat(warga1.id, JENIS_SKU, "A panjang")
        service.repository.create_surat(warga2.id, JENIS_SKU, "B panjang")

        client.force_login(warga1)

        response = client.get(reverse("surat-list"))

        data = response.json()["data"]

        assert len(data) == 1

    def test_admin_can_see_all_surat(self, user_factory):
        client = Client()

        admin = user_factory(role="ADMIN", is_staff=True)
        warga = user_factory(role="WARGA")

        from features.layanan_administrasi.services import SuratService
        service = SuratService()

        service.repository.create_surat(
            warga.id, JENIS_SKU, "Keperluan panjang"
        )

        client.force_login(admin)

        response = client.get(reverse("surat-list"))

        assert response.status_code == 200
        assert len(response.json()["data"]) >= 1

import uuid

@pytest.mark.django_db
class TestDetailSuratEdgeCase:

    def test_should_return_404_if_surat_not_found(self, user_factory):
        client = Client()
        warga = user_factory(role="WARGA")

        client.force_login(warga)

        fake_id = str(uuid.uuid4())  

        response = client.get(
            reverse("surat-detail", kwargs={"surat_id": fake_id})
        )

        assert response.status_code == 404

@pytest.mark.django_db
class TestDetailSuratSuccess:

    def test_warga_can_view_own_surat(self, user_factory):
        client = Client()
        warga = user_factory(role="WARGA")

        from features.layanan_administrasi.services import SuratService
        service = SuratService()

        surat = service.repository.create_surat(
            warga.id, JENIS_SKU, "Test"
        )

        client.force_login(warga)

        response = client.get(
            reverse("surat-detail", kwargs={"surat_id": str(surat.id)})
        )

        assert response.status_code == 200

@pytest.mark.django_db
class TestDetailSuratAdmin:

    def test_admin_can_view_any_surat(self, user_factory):
        client = Client()

        admin = user_factory(role="ADMIN", is_staff=True)
        warga = user_factory(role="WARGA")

        from features.layanan_administrasi.services import SuratService
        service = SuratService()

        surat = service.repository.create_surat(
            warga.id, JENIS_SKU, "Test"
        )

        client.force_login(admin)

        response = client.get(
            reverse("surat-detail", kwargs={"surat_id": str(surat.id)})
        )

        assert response.status_code == 200

@pytest.mark.django_db
class TestListSuratEmpty:

    def test_should_return_empty_list(self, user_factory):
        client = Client()
        warga = user_factory(role="WARGA")

        client.force_login(warga)

        response = client.get(reverse("surat-list"))

        assert response.status_code == 200
        assert response.json()["data"] == []

@pytest.mark.django_db
class TestAjukanSuratValidationEdge:

    def test_missing_keperluan_should_fail(self, user_factory):
        client = Client()
        warga = user_factory(role="WARGA")

        client.force_login(warga)

        response = client.post(
            reverse("surat-ajukan"),
            data=json.dumps({
                "jenis_surat": JENIS_SKU
            }),
            content_type="application/json",
        )

        assert response.status_code == 400