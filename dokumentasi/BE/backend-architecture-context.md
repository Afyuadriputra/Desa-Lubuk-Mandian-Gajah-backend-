# Backend Architecture Context

## 1. Ringkasan

Project backend ini adalah **Django 5 + Django Ninja + PostgreSQL** dengan pendekatan **feature modular**. Setiap fitur utama diletakkan di `backend/features/<nama_fitur>` dan umumnya mengikuti pola:

- `api.py`
- `schemas.py`
- `services.py`
- `domain.py`
- `repositories.py`
- `models.py`
- `permissions.py`
- `tests/`

Arsitektur aktual saat ini adalah **modular layered architecture yang pragmatis**, bukan clean architecture penuh seperti target literal PRD. Meski begitu, pembagian tanggung jawab sudah cukup konsisten dan testable.

Backend saat ini sudah mencakup:

- autentikasi dan manajemen akun
- profil desa dan wilayah
- publikasi informasi
- layanan administrasi surat
- pengaduan warga
- potensi ekonomi / BUMDes / wisata
- dashboard admin operasional

## 2. Stack dan Runtime

Core stack:

- Framework: `Django 5.0.3`
- API layer: `Django Ninja`
- Database: `PostgreSQL`
- Auth session: `django.contrib.auth` + custom user model
- Brute-force protection: `django-axes`
- Audit middleware: `django-auditlog`
- Logging app-level: `loguru` via `toolbox/logging`

Status infra:

- Redis: belum diaktifkan penuh, tapi cache API dashboard sudah siap memakai backend Django cache
- Celery: belum diaktifkan penuh
- S3-compatible storage: belum diaktifkan penuh
- Sentry: hook tersedia di toolbox, aktivasi tergantung env

## 3. Struktur Direktori Penting

```txt
backend/
├── core_django/
│   ├── settings.py
│   ├── urls.py
│   └── api_v1.py
├── toolbox/
│   ├── api/
│   ├── logging/
│   ├── pdf_generator/
│   ├── security/
│   └── storage/
├── features/
│   ├── auth_warga/
│   ├── dashboard_admin/
│   ├── layanan_administrasi/
│   ├── pengaduan_warga/
│   ├── potensi_ekonomi/
│   ├── profil_wilayah/
│   └── publikasi_informasi/
├── dokumentasi/
│   ├── BE/
│   └── FE/
└── tests/
```

## 4. Entry Point Request

Alur request HTTP:

1. Request masuk ke `core_django/urls.py`
2. Semua API diarahkan ke `/api/v1/`
3. Registry router ada di `core_django/api_v1.py`
4. Router feature dipasang dengan prefix masing-masing
5. Endpoint di `api.py` feature menerima request
6. `api.py` memvalidasi auth lewat security callable Ninja
7. Payload divalidasi oleh `schemas.py`
8. `services.py` menjalankan use case utama
9. `services.py` memanggil:
   - `domain.py` untuk business rule
   - `repositories.py` untuk akses ORM/database
   - `toolbox/*` untuk concern lintas fitur
10. Hasil dikembalikan ke `api.py` dan dirender oleh Ninja

Registry router saat ini:

- `/auth`
- `/dashboard-admin`
- `/layanan-administrasi`
- `/pengaduan`
- `/potensi-ekonomi`
- `/profil-wilayah`
- `/publikasi`

## 5. Kontrak Layer

### 5.1 `api.py`

Tanggung jawab:

- mendeklarasikan endpoint HTTP
- mengikat auth `AuthActiveUser`, `AuthAdminOnly`, `AuthBumdesManager`
- menerima query/path/body/file
- memanggil service
- memetakan response code dan shape output

Yang tidak boleh dominan di layer ini:

- query ORM langsung
- state machine bisnis
- permission bisnis kompleks

Catatan:

- beberapa feature punya 2 keluarga endpoint:
  - endpoint existing/original
  - endpoint `mvp/*` dengan envelope `{ "data": ... }` yang lebih stabil untuk frontend baru

### 5.2 `schemas.py`

Tanggung jawab:

- validasi payload masuk
- serialisasi output
- sanitasi input tertentu

Dipakai terutama untuk:

- validasi body JSON
- validasi `FormData`
- sanitasi HTML/XSS di publikasi, profil, potensi ekonomi

### 5.3 `services.py`

Ini pusat orkestrasi use case.

Tanggung jawab:

- cek permission bisnis
- panggil validator domain
- panggil repository
- audit event
- generate response object final
- integrasi helper toolbox seperti PDF dan upload validator

Prinsip umum:

- service tidak seharusnya tahu detail SQL
- service boleh memanggil banyak helper, tapi tetap harus menjaga fokus use case

### 5.4 `domain.py`

Berisi business rule murni tanpa ORM dan tanpa request object.

Contoh isi:

- validasi NIK
- state machine surat
- state machine pengaduan
- validasi input minimum
- kalkulasi SLA dashboard

### 5.5 `repositories.py`

Tanggung jawab:

- semua query ORM utama
- `create`, `update`, `get`, `list`, `delete`
- query agregasi untuk dashboard
- optimasi `select_related` / `prefetch_related`

### 5.6 `models.py`

Tanggung jawab:

- definisi tabel dan relasi Django ORM
- field database
- beberapa helper model sederhana

## 6. Toolbox Shared Utilities

`backend/toolbox` adalah shared layer lintas fitur.

### 6.1 `toolbox/api`

- auth callable untuk Django Ninja
- global exception handler

Auth callable penting:

- `AuthActiveUser`
- `AuthAdminOnly`
- `AuthBumdesManager`

### 6.2 `toolbox/security`

Berisi shared concern:

- `auth.py`: helper status auth dan role helper
- `permissions.py`: permission helper lintas role
- `checks.py`: helper validasi/cek akses tambahan
- `sanitizers.py`: sanitasi HTML/XSS
- `upload_validators.py`: validasi upload file

### 6.3 `toolbox/logging`

Komponen:

- `app_logger.py`: loguru logger
- `audit.py`: `audit_event(...)`
- `middleware.py`: request context middleware
- `request_context.py`: `request_id`, `user_id`, path, method
- `sentry.py`: bootstrap Sentry

Logging pattern:

- setiap request diberi `X-Request-ID`
- logger bind metadata `request_id`, `user_id`, `logger_name`
- aksi penting dicatat juga via `audit_event`

### 6.4 `toolbox/pdf_generator`

Digunakan terutama oleh modul surat.

Tugas:

- generate nomor surat
- render PDF
- naming/path helper

### 6.5 `toolbox/storage`

Berisi:

- path upload media
- validator storage/media
- helper media path

## 7. Security Model

### 7.1 Authentication

Auth saat ini berbasis **session Django**, bukan JWT.

Implikasi:

- login memakai `POST /api/v1/auth/login`
- logout memakai `POST /api/v1/auth/logout`
- validasi sesi aktif via `GET /api/v1/auth/me`
- frontend harus mengirim cookie session

### 7.2 Authorization

Role utama:

- `SUPERADMIN`
- `ADMIN`
- `BUMDES`
- `WARGA`

Aturan umum:

- `WARGA` hanya melihat data miliknya sendiri
- `ADMIN` dan `SUPERADMIN` mengelola modul desa
- `BUMDES` mengelola modul potensi ekonomi

### 7.3 Brute-force protection

`django-axes` aktif di settings.

Konfigurasi saat ini:

- `AXES_FAILURE_LIMIT = 5`
- `AXES_COOLOFF_TIME = 1`
- `AXES_RESET_ON_SUCCESS = True`

### 7.4 XSS dan upload safety

Sudah aktif:

- sanitasi HTML untuk konten publikasi, sebagian input profil, dan potensi ekonomi
- validasi file/image upload

## 8. Feature Modules

## 8.1 `auth_warga`

Tujuan:

- login/logout
- info user aktif
- create user warga
- create admin
- aktivasi/nonaktif akun
- ganti password

Komponen penting:

- `models.py`: `CustomUser`
- `domain.py`: validasi NIK, role, password change
- `permissions.py`: policy manage user
- `repositories.py`: lookup/update user
- `services.py`: login flow, activation, creation
- `api.py`: endpoint auth

Catatan implementasi:

- custom user pakai `nik` sebagai `USERNAME_FIELD`
- `UUID` sebagai primary key
- login memanggil `authenticate(...)`, lalu `login(request, user)`
- audit event dicatat untuk login success/fail dan perubahan akun

Endpoint penting:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/users/warga/create`
- `POST /api/v1/auth/users/admin/create`
- `POST /api/v1/auth/users/{user_id}/activate`
- `POST /api/v1/auth/users/{user_id}/deactivate`
- `POST /api/v1/auth/change-password`

## 8.2 `profil_wilayah`

Tujuan:

- kelola dusun
- kelola perangkat desa
- kelola profil desa
- expose profil publik

Komponen penting:

- `WilayahDusun`
- `WilayahPerangkat`
- `ProfilDesa`

Pattern:

- public profile diambil via endpoint publik
- dusun/perangkat/profil dikelola via endpoint admin
- upload foto perangkat memakai multipart

Catatan:

- endpoint publik saat ini mengembalikan `profil` + `perangkat`
- data perangkat publik hanya yang `is_published=True`

## 8.3 `publikasi_informasi`

Tujuan:

- kelola berita dan pengumuman
- expose konten publik yang published

Komponen penting:

- model tunggal `Publikasi`
- field pembeda `jenis`: `BERITA` / `PENGUMUMAN`
- status: `DRAFT` / `PUBLISHED`

Catatan:

- slug auto-generated di model
- service sanitasi HTML secara defensif
- public detail menyembunyikan status internal pada endpoint MVP

Endpoint publik:

- `GET /api/v1/publikasi/mvp/publik`
- `GET /api/v1/publikasi/mvp/publik/{slug}`

Endpoint admin:

- `POST /api/v1/publikasi/admin/buat`
- `PUT /api/v1/publikasi/admin/{slug}`
- `PUT /api/v1/publikasi/admin/{slug}/status`
- `DELETE /api/v1/publikasi/admin/{slug}`

## 8.4 `layanan_administrasi`

Tujuan:

- pengajuan surat warga
- tracking status
- proses admin
- generate dan download PDF

Jenis surat saat ini:

- `SKU`
- `SKTM`
- `DOMISILI`

Status surat:

- `PENDING`
- `VERIFIED`
- `PROCESSED`
- `DONE`
- `REJECTED`

Business rule penting:

- warga hanya melihat surat miliknya sendiri
- admin melihat semua
- transisi status harus valid
- `REJECTED` wajib punya alasan
- PDF hanya boleh tersedia saat `DONE`
- histori perubahan status disimpan

Komponen penting:

- `LayananSurat`
- `LayananSuratStatusHistory`
- domain state machine di `domain.py`
- PDF helper dari toolbox

Endpoint penting:

- `POST /api/v1/layanan-administrasi/mvp/surat/ajukan`
- `GET /api/v1/layanan-administrasi/mvp/surat`
- `GET /api/v1/layanan-administrasi/mvp/surat/{surat_id}`
- `POST /api/v1/layanan-administrasi/mvp/surat/{surat_id}/proses`
- `GET /api/v1/layanan-administrasi/mvp/surat/{surat_id}/download`

## 8.5 `pengaduan_warga`

Tujuan:

- buat pengaduan
- upload bukti
- tracking status
- tindak lanjut admin

Status pengaduan:

- `OPEN`
- `TRIAGED`
- `IN_PROGRESS`
- `RESOLVED`
- `CLOSED`

Business rule penting:

- warga hanya melihat pengaduannya sendiri
- admin melihat semua
- judul/deskripsi punya minimum validasi
- `RESOLVED` dan `CLOSED` wajib punya catatan
- histori tindak lanjut disimpan

Komponen penting:

- `LayananPengaduan`
- `LayananPengaduanHistory`
- validasi state machine di domain

Endpoint penting:

- `POST /api/v1/pengaduan/mvp/buat`
- `GET /api/v1/pengaduan/mvp`
- `GET /api/v1/pengaduan/mvp/{pengaduan_id}`
- `POST /api/v1/pengaduan/mvp/{pengaduan_id}/proses`

## 8.6 `potensi_ekonomi`

Tujuan:

- kelola katalog unit usaha desa / wisata
- tampilkan katalog publik

Kategori:

- `KOPERASI`
- `WISATA`
- `JASA`

Catatan:

- modul publik dan admin ada dalam feature yang sama
- endpoint publik bisa diakses anonim
- endpoint admin memakai role `BUMDES`, `ADMIN`, `SUPERADMIN`
- deskripsi dan fasilitas disanitasi di schema/service

Endpoint publik:

- `GET /api/v1/potensi-ekonomi/mvp/katalog`
- `GET /api/v1/potensi-ekonomi/mvp/{unit_id}`

Endpoint admin:

- `GET /api/v1/potensi-ekonomi/mvp/admin/list`
- `POST /api/v1/potensi-ekonomi/mvp/admin/buat`
- `PUT /api/v1/potensi-ekonomi/mvp/admin/{unit_id}`
- `DELETE /api/v1/potensi-ekonomi/mvp/admin/{unit_id}`

## 8.7 `dashboard_admin`

Tujuan:

- agregasi operasional admin
- bukan modul CRUD lintas fitur

Prinsip:

- dashboard mengonsumsi data dari modul lain
- dashboard memberi summary, queue, alert, activity, analytics, health
- CRUD tetap berada di feature domain masing-masing

Endpoint saat ini:

- `GET /api/v1/dashboard-admin/overview`
- `GET /api/v1/dashboard-admin/surat-queue`
- `GET /api/v1/dashboard-admin/pengaduan-queue`
- `GET /api/v1/dashboard-admin/recent-activity`
- `GET /api/v1/dashboard-admin/surat-analytics`
- `GET /api/v1/dashboard-admin/pengaduan-analytics`
- `GET /api/v1/dashboard-admin/content-health`
- `GET /api/v1/dashboard-admin/master-health`

Blok data overview:

- `summary`
- `alerts`
- `charts`
- `health`
- `quick_actions`

Query dashboard ditarik terutama dari:

- `LayananSurat`
- `LayananSuratStatusHistory`
- `LayananPengaduan`
- `LayananPengaduanHistory`
- `Publikasi`
- `BumdesUnitUsaha`
- `WilayahDusun`
- `WilayahPerangkat`
- `ProfilDesa`
- `CustomUser`

SLA operasional saat ini:

- `warning >= 24 jam`
- `overdue >= 72 jam`

## 9. Current API Conventions

Ada dua shape endpoint:

### 9.1 Shape original

Dipakai di endpoint lama, misalnya:

- list publikasi publik
- profil wilayah publik
- sebagian create/update lama

Contoh:

- list langsung berupa array
- object langsung berupa schema response

### 9.2 Shape MVP

Dipakai untuk frontend baru dan route name yang stabil.

Format:

```json
{
  "data": ...
}
```

Disarankan frontend baru memakai endpoint `mvp/*` saat tersedia karena shape lebih konsisten.

## 10. Request Flow Contoh Nyata

## 10.1 Login

1. `POST /auth/login`
2. `LoginIn` validasi payload
3. `AuthService.login_user(...)`
4. service normalisasi NIK
5. service cek user aktif
6. service panggil `authenticate(...)`
7. audit success/fail dicatat
8. `api.py` memanggil `login(request, user)`
9. session cookie aktif

## 10.2 Pengajuan surat

1. warga kirim `POST /layanan-administrasi/mvp/surat/ajukan`
2. schema validasi input
3. service validasi business rule
4. repository create `LayananSurat`
5. repository create histori awal
6. audit event dicatat
7. response envelope `{ data: surat }`

## 10.3 Proses pengaduan

1. admin kirim `POST /pengaduan/mvp/{id}/proses`
2. schema validasi status + notes
3. service cek izin admin
4. domain validasi transisi status
5. domain validasi notes untuk `RESOLVED/CLOSED`
6. repository update pengaduan
7. repository create histori
8. audit event dicatat

## 10.4 Dashboard overview

1. admin akses `GET /dashboard-admin/overview`
2. auth `AuthAdminOnly`
3. service cek akses dashboard
4. repository tarik summary, chart, trend, health
5. domain hitung SLA / aging / completeness
6. service build `alerts` dan `quick_actions`
7. hasil bisa di-cache via `django.core.cache`

## 11. Testing Strategy Aktual

Test saat ini mencakup:

- unit test domain
- service test
- repository test
- API test
- integration flow test
- PRD compliance test
- dashboard service/API test

Suite yang sudah terverifikasi hijau pada checkpoint terakhir:

- feature tests untuk auth, dashboard, surat, pengaduan, publikasi, ekonomi, profil
- integration tests
- PRD compliance tests

Angka checkpoint terakhir:

- `164 passed`

## 12. Kesenjangan antara PRD dan Implementasi Aktual

Yang sudah dekat PRD:

- modul inti MVP
- security dasar
- audit event
- brute-force protection
- dashboard operasional admin

Yang belum penuh:

- Redis aktif penuh
- Celery aktif penuh
- S3 storage aktif penuh
- audit log viewer endpoint eksplisit
- dashboard phase 2 yang lebih dalam
- notifikasi WA/email
- QR verification surat
- multi-template surat

## 13. Known Architectural Decisions

Keputusan penting yang sengaja diambil:

- memakai **session auth**, bukan JWT
- mempertahankan endpoint lama untuk kompatibilitas
- menambah endpoint `mvp/*` untuk shape yang lebih stabil
- tidak memaksa semua feature jadi clean architecture literal
- fokus ke **layered modular pragmatic design**
- dashboard admin hanya aggregator, bukan modul CRUD lintas fitur

## 14. Known Weak Spots

Bagian yang perlu diingat LLM berikutnya:

- `dashboard_admin/services.py` sudah cukup besar; masih sehat, tapi mulai mendekati batas nyaman SRP
- beberapa modul masih punya shape response campuran antara endpoint lama dan endpoint `mvp/*`
- modul `profil_wilayah` publik belum memakai envelope `{ data: ... }`
- backend belum punya endpoint list user admin/warga lengkap untuk admin panel yang lebih kaya
- caching dashboard sudah siap, tapi backend cache production belum diaktifkan penuh

## 15. Guidance untuk LLM Berikutnya

Kalau LLM berikutnya diminta mengubah backend ini, asumsi aman:

- jangan rusak endpoint lama
- bila menambah API untuk frontend baru, prefer shape `{ "data": ... }`
- hormati pembagian file:
  - `api.py` tipis
  - `schemas.py` validasi/serialisasi
  - `services.py` orkestrasi
  - `domain.py` business rule
  - `repositories.py` ORM access
- jangan pindahkan logic ORM ke `api.py`
- jangan duplikasi permission lintas feature bila sudah ada helper di toolbox
- untuk admin dashboard, tambah agregasi di repository dan mapping di service, bukan CRUD baru

## 16. File Referensi yang Paling Penting

Untuk memahami backend secara cepat, baca file berikut lebih dulu:

- [settings.py](/mnt/d/kuliah/joki/radit/desa/backend/core_django/settings.py:1)
- [urls.py](/mnt/d/kuliah/joki/radit/desa/backend/core_django/urls.py:1)
- [api_v1.py](/mnt/d/kuliah/joki/radit/desa/backend/core_django/api_v1.py:1)
- [toolbox/api/auth.py](/mnt/d/kuliah/joki/radit/desa/backend/toolbox/api/auth.py:1)
- [auth_warga/services.py](/mnt/d/kuliah/joki/radit/desa/backend/features/auth_warga/services.py:1)
- [layanan_administrasi/services.py](/mnt/d/kuliah/joki/radit/desa/backend/features/layanan_administrasi/services.py:1)
- [pengaduan_warga/services.py](/mnt/d/kuliah/joki/radit/desa/backend/features/pengaduan_warga/services.py:1)
- [dashboard_admin/services.py](/mnt/d/kuliah/joki/radit/desa/backend/features/dashboard_admin/services.py:1)

## 17. Kesimpulan

Backend ini adalah sistem Django modular yang sudah cukup matang untuk MVP portal desa. Pola utamanya konsisten: feature-based, layered, dan pragmatis. Bagi LLM atau developer baru, cara terbaik memahami sistem ini adalah melihatnya sebagai:

- **Django monolith modular**
- dengan **feature isolation**
- **service-oriented orchestration**
- **domain validation**
- **repository-based ORM access**
- **session auth**
- **public API + admin API + dashboard aggregator**

Dokumen ini adalah konteks implementasi aktual, bukan blueprint ideal. Bila PRD dan codebase berbeda, prioritaskan codebase dan test suite sebagai source of truth operasional.
