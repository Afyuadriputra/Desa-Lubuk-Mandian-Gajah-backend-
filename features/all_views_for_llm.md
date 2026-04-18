# Django Views Collection for LLM

Generated at: 2026-04-17T14:12:50
Base directory: `D:\Kuliah\joki\radit\desa\backend\features`

## Daftar Feature

- `auth_warga`
- `dashboard_admin`
- `layanan_administrasi`
- `pengaduan_warga`
- `potensi_ekonomi`
- `profil_wilayah`
- `publikasi_informasi`

---

## 1. Feature: `auth_warga`

**Path:** `D:\Kuliah\joki\radit\desa\backend\features\auth_warga\views.py`

```python
# features/auth_warga/views.py

import json

from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.auth_warga.domain import (
    AuthenticationFailedError,
    DuplicateNIKError,
    InactiveAccountError,
    InvalidNIKError,
    InvalidRoleError,
)
from features.auth_warga.services import (
    AuthService,
    PermissionDeniedError,
    UserNotFoundError,
)
from toolbox.security.auth import is_active_user

auth_service = AuthService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def login_view(request):
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    nik = payload.get("nik", "")
    password = payload.get("password", "")

    if not nik or not password:
        return JsonResponse({"detail": "NIK dan kata sandi wajib diisi."}, status=400)

    try:
        result = auth_service.login_user(
            request=request,
            nik=nik,
            password=password,
        )
    except InvalidNIKError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except InactiveAccountError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except AuthenticationFailedError as exc:
        return JsonResponse({"detail": str(exc)}, status=401)

    login(request, result.user)
    return JsonResponse(
        {
            "detail": result.message,
            "data": {
                "id": str(result.user.id),
                "nik": result.user.nik,
                "nama_lengkap": result.user.nama_lengkap,
                "role": result.user.role,
                "is_active": result.user.is_active,
            },
        },
        status=200,
    )


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "Logout berhasil."}, status=200)


@require_GET
def me_view(request):
    user = getattr(request, "user", None)
    if not is_active_user(user):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    return JsonResponse(
        {
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "nomor_hp": user.nomor_hp,
                "role": user.role,
                "is_active": user.is_active,
            }
        },
        status=200,
    )


@require_POST
def create_warga_user_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        user = auth_service.create_warga_account(
            actor=actor,
            nik=payload.get("nik", ""),
            password=payload.get("password", ""),
            nama_lengkap=payload.get("nama_lengkap", ""),
            nomor_hp=payload.get("nomor_hp"),
            is_active=payload.get("is_active", True),
        )
    except (InvalidNIKError, DuplicateNIKError, InvalidRoleError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "detail": "Akun warga berhasil dibuat.",
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "role": user.role,
                "is_active": user.is_active,
            },
        },
        status=201,
    )


@require_POST
def create_admin_user_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        user = auth_service.create_admin_account(
            actor=actor,
            nik=payload.get("nik", ""),
            password=payload.get("password", ""),
            nama_lengkap=payload.get("nama_lengkap", ""),
            role=payload.get("role", ""),
            nomor_hp=payload.get("nomor_hp"),
            is_active=payload.get("is_active", True),
        )
    except (InvalidNIKError, DuplicateNIKError, InvalidRoleError) as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "detail": "Akun admin berhasil dibuat.",
            "data": {
                "id": str(user.id),
                "nik": user.nik,
                "nama_lengkap": user.nama_lengkap,
                "role": user.role,
                "is_active": user.is_active,
            },
        },
        status=201,
    )


@require_POST
def activate_user_view(request, user_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        target_user = auth_service.activate_account(actor=actor, target_user_id=user_id)
    except UserNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Akun berhasil diaktifkan.",
            "data": {
                "id": str(target_user.id),
                "nik": target_user.nik,
                "nama_lengkap": target_user.nama_lengkap,
                "role": target_user.role,
                "is_active": target_user.is_active,
            },
        },
        status=200,
    )


@require_POST
def deactivate_user_view(request, user_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        target_user = auth_service.deactivate_account(actor=actor, target_user_id=user_id)
    except UserNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Akun berhasil dinonaktifkan.",
            "data": {
                "id": str(target_user.id),
                "nik": target_user.nik,
                "nama_lengkap": target_user.nama_lengkap,
                "role": target_user.role,
                "is_active": target_user.is_active,
            },
        },
        status=200,
    )
```

---

## 2. Feature: `dashboard_admin`

**Path:** `D:\Kuliah\joki\radit\desa\backend\features\dashboard_admin\views.py`

```python
# features/dashboard_admin/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from features.dashboard_admin.domain import DashboardAccessError
from features.dashboard_admin.services import DashboardService
from toolbox.security.auth import is_active_user

dashboard_service = DashboardService()

@require_GET
def analitik_dashboard_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)
    
    try:
        data = dashboard_service.get_analitik_lengkap(actor)
        return JsonResponse({"data": data}, status=200)
    except DashboardAccessError as e:
        return JsonResponse({"detail": str(e)}, status=403)
    except Exception as e:
        # Penanganan error global (KISS) agar server tidak crash jika query gagal
        return JsonResponse({"detail": "Terjadi kesalahan pada server saat memuat analitik."}, status=500)
```

---

## 3. Feature: `layanan_administrasi`

**Path:** `D:\Kuliah\joki\radit\desa\backend\features\layanan_administrasi\views.py`

```python
# features/layanan_administrasi/views.py

import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.layanan_administrasi.domain import LayananSuratError
from features.layanan_administrasi.services import (
    LayananSuratNotFoundError,
    PermissionDeniedError,
    SuratService,
)
from toolbox.security.auth import is_active_user

surat_service = SuratService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def ajukan_surat_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        surat = surat_service.ajukan_surat(
            actor=actor,
            jenis_surat=payload.get("jenis_surat", ""),
            keperluan=payload.get("keperluan", "")
        )
    except LayananSuratError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Pengajuan surat berhasil.",
            "data": {
                "id": str(surat.id),
                "jenis_surat": surat.jenis_surat,
                "status": surat.status,
                "created_at": surat.created_at.isoformat(),
            }
        },
        status=201
    )


@require_GET
def list_surat_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    qs = surat_service.list_surat(actor)
    data = [
        {
            "id": str(s.id),
            "jenis_surat": s.jenis_surat,
            "status": s.status,
            "pemohon": s.pemohon.nama_lengkap,
            "created_at": s.created_at.isoformat(),
        } for s in qs
    ]

    return JsonResponse({"data": data}, status=200)


@require_GET
def detail_surat_view(request, surat_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        surat = surat_service.get_surat_detail(actor, surat_id)
    except LayananSuratNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "data": {
                "id": str(surat.id),
                "jenis_surat": surat.jenis_surat,
                "keperluan": surat.keperluan,
                "status": surat.status,
                "nomor_surat": surat.nomor_surat,
                "rejection_reason": surat.rejection_reason,
                "pdf_url": surat.pdf_file.url if surat.pdf_file else None,
                "pemohon": {
                    "id": str(surat.pemohon.id),
                    "nama_lengkap": surat.pemohon.nama_lengkap,
                    "nik": surat.pemohon.nik,
                },
                "created_at": surat.created_at.isoformat(),
                "updated_at": surat.updated_at.isoformat(),
            }
        },
        status=200
    )


@require_POST
def proses_surat_view(request, surat_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        surat = surat_service.proses_surat(
            actor=actor,
            surat_id=surat_id,
            new_status=payload.get("status", ""),
            notes=payload.get("notes"),
            nomor_surat=payload.get("nomor_surat"),
            rejection_reason=payload.get("rejection_reason")
        )
    except LayananSuratError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except LayananSuratNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    return JsonResponse(
        {
            "detail": "Status surat berhasil diperbarui.",
            "data": {
                "id": str(surat.id),
                "status": surat.status,
            }
        },
        status=200
    )
```

---

## 4. Feature: `pengaduan_warga`

**Path:** `D:\Kuliah\joki\radit\desa\backend\features\pengaduan_warga\views.py`

```python
# features/pengaduan_warga/views.py

import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.pengaduan_warga.domain import PengaduanError
from features.pengaduan_warga.services import (
    FileUploadError,
    PengaduanNotFoundError,
    PengaduanService,
    PermissionDeniedError,
)
from toolbox.security.auth import is_active_user

pengaduan_service = PengaduanService()


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


@require_POST
def buat_pengaduan_view(request):
    """Menerima Multipart/Form-Data karena ada upload gambar opsional."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    kategori = request.POST.get("kategori", "")
    judul = request.POST.get("judul", "")
    deskripsi = request.POST.get("deskripsi", "")
    foto_bukti = request.FILES.get("foto_bukti")

    try:
        pengaduan = pengaduan_service.buat_pengaduan(
            actor=actor,
            kategori=kategori,
            judul=judul,
            deskripsi=deskripsi,
            foto_bukti=foto_bukti
        )
    except PengaduanError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except FileUploadError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Pengaduan berhasil dibuat.",
            "data": {
                "id": pengaduan.id,
                "status": pengaduan.status,
                "kategori": pengaduan.kategori,
                "created_at": pengaduan.created_at.isoformat(),
            }
        },
        status=201
    )


@require_GET
def list_pengaduan_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    qs = pengaduan_service.list_pengaduan(actor)
    data = [
        {
            "id": p.id,
            "judul": p.judul,
            "kategori": p.kategori,
            "status": p.status,
            "pelapor": p.pelapor.nama_lengkap,
            "created_at": p.created_at.isoformat(),
        } for p in qs
    ]

    return JsonResponse({"data": data}, status=200)


@require_GET
def detail_pengaduan_view(request, pengaduan_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        pengaduan = pengaduan_service.get_pengaduan_detail(actor, pengaduan_id)
    except PengaduanNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    histori = [
        {
            "status_to": h.status_to,
            "notes": h.notes,
            "created_at": h.created_at.isoformat(),
            "changed_by": h.changed_by.nama_lengkap if h.changed_by else "System"
        }
        for h in pengaduan.histori_tindak_lanjut.all()
    ]

    return JsonResponse(
        {
            "data": {
                "id": pengaduan.id,
                "kategori": pengaduan.kategori,
                "judul": pengaduan.judul,
                "deskripsi": pengaduan.deskripsi,
                "status": pengaduan.status,
                "foto_bukti_url": pengaduan.foto_bukti.url if pengaduan.foto_bukti else None,
                "pelapor": {
                    "nama_lengkap": pengaduan.pelapor.nama_lengkap,
                },
                "histori": histori,
                "created_at": pengaduan.created_at.isoformat(),
                "updated_at": pengaduan.updated_at.isoformat(),
            }
        },
        status=200
    )


@require_POST
def proses_pengaduan_view(request, pengaduan_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Payload JSON tidak valid."}, status=400)

    try:
        pengaduan = pengaduan_service.proses_pengaduan(
            actor=actor,
            pengaduan_id=pengaduan_id,
            new_status=payload.get("status", ""),
            notes=payload.get("notes")
        )
    except PengaduanError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)
    except PengaduanNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)

    return JsonResponse(
        {
            "detail": "Status pengaduan berhasil diperbarui.",
            "data": {
                "id": pengaduan.id,
                "status": pengaduan.status,
            }
        },
        status=200
    )
```

---

## 5. Feature: `potensi_ekonomi`

**Path:** `D:\Kuliah\joki\radit\desa\backend\features\potensi_ekonomi\views.py`

```python
# features/potensi_ekonomi/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from features.potensi_ekonomi.domain import PotensiEkonomiError
from features.potensi_ekonomi.services import (
    FileUploadError,
    PermissionDeniedError,
    PotensiEkonomiService,
    UnitUsahaNotFoundError,
)
from toolbox.security.auth import is_active_user

ekonomi_service = PotensiEkonomiService()


@require_GET
def katalog_publik_view(request):
    """Endpoint untuk warga melihat katalog BUMDes/Wisata yang aktif."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        qs = ekonomi_service.get_katalog_publik(actor)
        data = [
            {
                "id": u.id,
                "nama_usaha": u.nama_usaha,
                "kategori": u.kategori,
                "deskripsi": u.deskripsi,
                "harga_tiket": u.harga_tiket,
                "foto_url": u.foto_utama.url if u.foto_utama else None,
            } for u in qs
        ]
        return JsonResponse({"data": data}, status=200)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)


@require_GET
def list_admin_view(request):
    """Endpoint untuk admin melihat semua data (termasuk draft)."""
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        qs = ekonomi_service.get_semua_unit_admin(actor)
        data = [
            {
                "id": u.id,
                "nama_usaha": u.nama_usaha,
                "kategori": u.kategori,
                "is_published": u.is_published,
                "created_at": u.created_at.isoformat(),
            } for u in qs
        ]
        return JsonResponse({"data": data}, status=200)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)


@require_POST
def buat_unit_usaha_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    # Menangani form-data karena ada upload gambar
    data_payload = {
        "nama_usaha": request.POST.get("nama_usaha"),
        "kategori": request.POST.get("kategori"),
        "deskripsi": request.POST.get("deskripsi"),
        "fasilitas": request.POST.get("fasilitas"),
        "kontak_wa": request.POST.get("kontak_wa"),
        "harga_tiket": request.POST.get("harga_tiket"),
        "is_published": request.POST.get("is_published", "false"),
    }
    foto = request.FILES.get("foto_utama")

    try:
        unit = ekonomi_service.buat_unit_usaha(actor, data_payload, foto)
    except PotensiEkonomiError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except FileUploadError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "detail": "Data BUMDes/Wisata berhasil ditambahkan.",
            "data": {
                "id": unit.id,
                "nama_usaha": unit.nama_usaha,
                "is_published": unit.is_published,
            }
        },
        status=201
    )


@require_GET
def detail_unit_view(request, unit_id):
    actor = getattr(request, "user", None)
    if not is_active_user(actor):
        return JsonResponse({"detail": "Unauthorized."}, status=401)

    try:
        unit = ekonomi_service.get_detail_unit(actor, unit_id)
    except UnitUsahaNotFoundError as exc:
        return JsonResponse({"detail": str(exc)}, status=404)
    except PermissionDeniedError as exc:
        return JsonResponse({"detail": str(exc)}, status=403)

    return JsonResponse(
        {
            "data": {
                "id": unit.id,
                "nama_usaha": unit.nama_usaha,
                "kategori": unit.kategori,
                "deskripsi": unit.deskripsi,
                "fasilitas": unit.fasilitas,
                "kontak_wa": unit.kontak_wa,
                "harga_tiket": unit.harga_tiket,
                "is_published": unit.is_published,
                "foto_url": unit.foto_utama.url if unit.foto_utama else None,
            }
        },
        status=200
    )
```

---

## 6. Feature: `profil_wilayah`

**Path:** `D:\Kuliah\joki\radit\desa\backend\features\profil_wilayah\views.py`

```python
# features/profil_wilayah/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from features.profil_wilayah.services import DusunService, PerangkatService, ProfilDesaService
from toolbox.security.auth import is_active_user

dusun_service = DusunService()
perangkat_service = PerangkatService()
profil_service = ProfilDesaService()

@require_GET
def profil_publik_view(request):
    """Menampilkan Visi, Misi, Sejarah dan Perangkat Desa yang aktif."""
    profil = profil_service.get_profil()
    perangkat = perangkat_service.get_perangkat_publik()
    
    return JsonResponse({
        "profil": {"visi": profil.visi, "misi": profil.misi, "sejarah": profil.sejarah},
        "perangkat": [{"jabatan": p.jabatan, "nama": p.user.nama_lengkap, "foto_url": p.foto.url if p.foto else None} for p in perangkat]
    }, status=200)

@require_POST
def tambah_dusun_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): return JsonResponse({"detail": "Unauthorized"}, status=401)
    
    data = json.loads(request.body.decode("utf-8") or "{}")
    try:
        dusun = dusun_service.tambah_dusun(actor, data.get("nama_dusun"), data.get("kepala_dusun"))
        return JsonResponse({"detail": "Dusun berhasil ditambahkan", "id": dusun.id}, status=201)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)

@require_POST
def tambah_perangkat_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): return JsonResponse({"detail": "Unauthorized"}, status=401)
    
    try:
        perangkat = perangkat_service.tambah_perangkat(
            actor=actor,
            user_id=request.POST.get("user_id"),
            jabatan=request.POST.get("jabatan"),
            is_published=request.POST.get("is_published", "false").lower() == "true",
            foto=request.FILES.get("foto")
        )
        return JsonResponse({"detail": "Perangkat berhasil ditambahkan", "id": perangkat.id}, status=201)
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)
```

---

## 7. Feature: `publikasi_informasi`

**Path:** `D:\Kuliah\joki\radit\desa\backend\features\publikasi_informasi\views.py`

```python
# features/publikasi_informasi/views.py

import json
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from features.publikasi_informasi.services import PublikasiService, PublikasiError, PublikasiAccessError
from toolbox.security.auth import is_active_user

publikasi_service = PublikasiService()

@require_GET
def list_publikasi_publik_view(request):
    jenis = request.GET.get("jenis") # Opsional: ?jenis=BERITA
    qs = publikasi_service.get_publikasi_publik(jenis)
    data = [{
        "judul": p.judul, 
        "slug": p.slug, 
        "jenis": p.jenis,
        "penulis": p.penulis.nama_lengkap if p.penulis else "Admin",
        "published_at": p.published_at.isoformat() if p.published_at else None
    } for p in qs]
    return JsonResponse({"data": data}, status=200)

@require_GET
def detail_publikasi_view(request, slug):
    try:
        p = publikasi_service.get_detail_publik(slug)
        return JsonResponse({
            "data": {
                "judul": p.judul,
                "konten_html": p.konten_html, # Aman, sudah disanitasi saat disave
                "jenis": p.jenis,
                "penulis": p.penulis.nama_lengkap if p.penulis else "Admin",
                "published_at": p.published_at.isoformat() if p.published_at else None
            }
        }, status=200)
    except PublikasiError as e:
        return JsonResponse({"detail": str(e)}, status=404)

@require_POST
def buat_publikasi_admin_view(request):
    actor = getattr(request, "user", None)
    if not is_active_user(actor): 
        return JsonResponse({"detail": "Unauthorized"}, status=401)
        
    data = json.loads(request.body.decode("utf-8") or "{}")
    try:
        publikasi = publikasi_service.buat_publikasi(
            actor=actor,
            judul=data.get("judul"),
            konten_html=data.get("konten_html"),
            jenis=data.get("jenis", "BERITA"),
            status=data.get("status", "DRAFT")
        )
        return JsonResponse({"detail": "Publikasi berhasil dibuat", "slug": publikasi.slug}, status=201)
    except (PublikasiError, PublikasiAccessError) as e:
        return JsonResponse({"detail": str(e)}, status=400)
```

---
