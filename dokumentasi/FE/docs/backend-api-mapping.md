# Backend API Mapping for Frontend

Dokumen ini memetakan halaman frontend Next.js/React + TypeScript ke endpoint backend Django Ninja yang sudah tersedia di project.

Base API:

```txt
/api/v1
```

Default env frontend:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Auth dan sesi

Backend saat ini memakai session Django, bukan JWT.

- Frontend harus kirim request dengan `credentials: "include"`
- Untuk request mutasi `POST`, `PUT`, `DELETE`, siapkan CSRF bila frontend dijalankan beda origin/domain dari backend
- Endpoint cek sesi aktif:
  - `GET /auth/me`

## Struktur client yang dibuat

Folder client TS:

```txt
frontend/my-project/lib/api/
├── client.ts
├── types.ts
├── auth.ts
├── profil.ts
├── publikasi.ts
├── ekonomi.ts
├── surat.ts
├── pengaduan.ts
├── dashboard.ts
├── homepage.ts
└── index.ts
```

## Mapping halaman frontend ke backend

### Halaman yang sudah ada sekarang

| Frontend page | Tujuan | Endpoint backend utama | Client TS |
| --- | --- | --- | --- |
| `/` | Homepage website publik | `GET /profil-wilayah/publik` | `profilApi.getPublik()` |
| `/` | Homepage website publik | `GET /publikasi/mvp/publik` | `publikasiApi.listPublik()` |
| `/` | Homepage website publik | `GET /potensi-ekonomi/mvp/katalog` | `ekonomiApi.listPublik()` |

Catatan:

- Saat ini [homepage.data.ts](</mnt/d/kuliah/joki/radit/desa/frontend/my-project/app/(website)/homepage/data/homepage.data.ts:1>) masih statis.
- Helper `getHomepageBackendData()` di [homepage.ts](/mnt/d/kuliah/joki/radit/desa/frontend/my-project/lib/api/homepage.ts:1) sudah disiapkan untuk migrasi bertahap.

### Rekomendasi page website publik

| Frontend page | Endpoint backend | Client TS |
| --- | --- | --- |
| `/berita` | `GET /publikasi/mvp/publik` | `publikasiApi.listPublik()` |
| `/berita/[slug]` | `GET /publikasi/mvp/publik/{slug}` | `publikasiApi.detailPublik(slug)` |
| `/pengumuman` | `GET /publikasi/mvp/publik` + filter frontend `jenis=PENGUMUMAN` | `publikasiApi.listPublik()` |
| `/potensi` | `GET /potensi-ekonomi/mvp/katalog` | `ekonomiApi.listPublik()` |
| `/potensi/[id]` | `GET /potensi-ekonomi/mvp/{id}` | `ekonomiApi.detailPublik(id)` |
| `/profil-desa` | `GET /profil-wilayah/publik` | `profilApi.getPublik()` |

### Rekomendasi page portal warga

| Frontend page | Endpoint backend | Client TS |
| --- | --- | --- |
| `/login` | `POST /auth/login` | `authApi.login()` |
| `/akun` | `GET /auth/me` | `authApi.me()` |
| `/akun/password` | `POST /auth/change-password` | `authApi.changePassword()` |
| `/surat` | `GET /layanan-administrasi/mvp/surat` | `suratApi.list()` |
| `/surat/ajukan` | `POST /layanan-administrasi/mvp/surat/ajukan` | `suratApi.ajukan()` |
| `/surat/[id]` | `GET /layanan-administrasi/mvp/surat/{id}` | `suratApi.detail(id)` |
| `/surat/[id]/download` | `GET /layanan-administrasi/mvp/surat/{id}/download` | `suratApi.getDownloadUrl(id)` |
| `/pengaduan` | `GET /pengaduan/mvp` | `pengaduanApi.list()` |
| `/pengaduan/buat` | `POST /pengaduan/mvp/buat` | `pengaduanApi.buat()` |
| `/pengaduan/[id]` | `GET /pengaduan/mvp/{id}` | `pengaduanApi.detail(id)` |

### Rekomendasi page admin panel

| Frontend page | Endpoint backend | Client TS |
| --- | --- | --- |
| `/admin` | `GET /dashboard-admin/overview` | `dashboardApi.overview()` |
| `/admin/surat-queue` | `GET /dashboard-admin/surat-queue` | `dashboardApi.suratQueue(filters)` |
| `/admin/pengaduan-queue` | `GET /dashboard-admin/pengaduan-queue` | `dashboardApi.pengaduanQueue(filters)` |
| `/admin/activity` | `GET /dashboard-admin/recent-activity` | `dashboardApi.recentActivity(limit)` |
| `/admin/analytics/surat` | `GET /dashboard-admin/surat-analytics` | `dashboardApi.suratAnalytics(days)` |
| `/admin/analytics/pengaduan` | `GET /dashboard-admin/pengaduan-analytics` | `dashboardApi.pengaduanAnalytics(days)` |
| `/admin/health/content` | `GET /dashboard-admin/content-health` | `dashboardApi.contentHealth()` |
| `/admin/health/master` | `GET /dashboard-admin/master-health` | `dashboardApi.masterHealth()` |
| `/admin/publikasi` | `GET /publikasi/mvp/publik` atau list admin custom nanti | `publikasiApi.listPublik()` |
| `/admin/publikasi/buat` | `POST /publikasi/admin/buat` | `publikasiApi.create()` |
| `/admin/publikasi/[slug]` | `PUT /publikasi/admin/{slug}` | `publikasiApi.update(slug)` |
| `/admin/publikasi/[slug]/status` | `PUT /publikasi/admin/{slug}/status` | `publikasiApi.updateStatus(slug)` |
| `/admin/publikasi/[slug]/hapus` | `DELETE /publikasi/admin/{slug}` | `publikasiApi.remove(slug)` |
| `/admin/dusun` | `GET /profil-wilayah/admin/dusun` | `profilApi.listDusunAdmin()` |
| `/admin/dusun/buat` | `POST /profil-wilayah/admin/dusun` | `profilApi.createDusun()` |
| `/admin/dusun/[id]` | `PUT /profil-wilayah/admin/dusun/{id}` | `profilApi.updateDusun(id)` |
| `/admin/profil-desa` | `PUT /profil-wilayah/admin/profil` | `profilApi.updateProfilDesa()` |
| `/admin/ekonomi` | `GET /potensi-ekonomi/mvp/admin/list` | `ekonomiApi.listAdmin()` |
| `/admin/ekonomi/buat` | `POST /potensi-ekonomi/mvp/admin/buat` | `ekonomiApi.create()` |
| `/admin/ekonomi/[id]` | `PUT /potensi-ekonomi/mvp/admin/{id}` | `ekonomiApi.update(id)` |
| `/admin/ekonomi/[id]/hapus` | `DELETE /potensi-ekonomi/mvp/admin/{id}` | `ekonomiApi.remove(id)` |
| `/admin/surat` | `GET /layanan-administrasi/mvp/surat` | `suratApi.list()` |
| `/admin/surat/[id]` | `GET /layanan-administrasi/mvp/surat/{id}` | `suratApi.detail(id)` |
| `/admin/surat/[id]/proses` | `POST /layanan-administrasi/mvp/surat/{id}/proses` | `suratApi.proses(id)` |
| `/admin/pengaduan` | `GET /pengaduan/mvp` | `pengaduanApi.list()` |
| `/admin/pengaduan/[id]` | `GET /pengaduan/mvp/{id}` | `pengaduanApi.detail(id)` |
| `/admin/pengaduan/[id]/proses` | `POST /pengaduan/mvp/{id}/proses` | `pengaduanApi.proses(id)` |
| `/admin/users/warga/buat` | `POST /auth/users/warga/create` | `authApi.createWarga()` |
| `/admin/users/admin/buat` | `POST /auth/users/admin/create` | `authApi.createAdmin()` |
| `/admin/users/[id]/activate` | `POST /auth/users/{id}/activate` | `authApi.activateUser(id)` |
| `/admin/users/[id]/deactivate` | `POST /auth/users/{id}/deactivate` | `authApi.deactivateUser(id)` |

## Endpoint prioritas untuk website sekarang

Kalau target dekat kamu adalah website publik dulu, cukup setup ini dulu:

1. `profilApi.getPublik()`
2. `publikasiApi.listPublik()`
3. `publikasiApi.detailPublik(slug)`
4. `ekonomiApi.listPublik()`
5. `ekonomiApi.detailPublik(id)`

## Contoh pemakaian

### Server component Next.js

```tsx
import { getHomepageBackendData } from "@/lib/api";

export default async function HomePage() {
  const data = await getHomepageBackendData();
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
```

### Login action

```ts
import { authApi } from "@/lib/api/auth";

await authApi.login({
  nik: "1234123412341234",
  password: "password123",
});
```

## Catatan implementasi

- Sebagian endpoint publik lama tidak memakai envelope `{ data: ... }`, tapi client baru dipusatkan ke endpoint yang paling stabil untuk frontend baru.
- Modul `profil_wilayah` publik saat ini belum dibungkus envelope; itu normal karena memang shape existing backend begitu.
- Kalau nanti frontend admin butuh list user admin/warga penuh, backend masih perlu endpoint list/search user khusus admin.
- Kalau frontend butuh pagination, search, dan filter list publikasi/surat/pengaduan yang lebih kaya, backend sebaiknya ditambah query params resmi.
