export type ApiEnvelope<T> = {
  data: T;
};

export type ApiError = {
  detail: string;
};

export type UserRole = "SUPERADMIN" | "ADMIN" | "BUMDES" | "WARGA";

export type UserDto = {
  id: string;
  nik: string;
  nama_lengkap: string;
  nomor_hp?: string | null;
  role: UserRole;
  is_active: boolean;
};

export type ActivationDto = UserDto;

export type ProfilDesaDto = {
  visi: string;
  misi: string;
  sejarah: string;
};

export type DusunDto = {
  id: number;
  nama_dusun: string;
  kepala_dusun: string;
};

export type PerangkatPublikDto = {
  id: number;
  nama_lengkap: string;
  jabatan: string;
  foto_url?: string | null;
};

export type ProfilPublikDto = {
  profil_desa: ProfilDesaDto | null;
  dusun: DusunDto[];
  perangkat: PerangkatPublikDto[];
};

export type PublikasiListItemDto = {
  id: number;
  judul: string;
  slug: string;
  jenis: "BERITA" | "PENGUMUMAN";
  ringkasan?: string | null;
  published_at?: string | null;
  created_at?: string | null;
};

export type PublikasiDetailDto = {
  id: number;
  judul: string;
  slug: string;
  jenis: "BERITA" | "PENGUMUMAN";
  konten_html: string;
  published_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type UnitUsahaListItemDto = {
  id: number;
  nama_usaha: string;
  kategori: "KOPERASI" | "WISATA" | "JASA";
  deskripsi: string;
  fasilitas?: string | null;
  kontak_wa?: string | null;
  harga_tiket?: string | number | null;
  foto_utama_url?: string | null;
  is_published?: boolean;
};

export type UnitUsahaDetailDto = UnitUsahaListItemDto & {
  created_at?: string | null;
  updated_at?: string | null;
};

export type SuratDto = {
  id: string;
  jenis_surat: "SKU" | "SKTM" | "DOMISILI";
  keperluan: string;
  status: "PENDING" | "VERIFIED" | "PROCESSED" | "DONE" | "REJECTED";
  nomor_surat?: string | null;
  rejection_reason?: string | null;
  pdf_url?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type SuratHistoryDto = {
  status_from?: string | null;
  status_to: string;
  notes?: string | null;
  created_at: string;
  changed_by?: string | null;
};

export type SuratDetailDto = SuratDto & {
  histori_status?: SuratHistoryDto[];
};

export type PengaduanDto = {
  id: number;
  kategori: string;
  judul: string;
  deskripsi: string;
  status: "OPEN" | "TRIAGED" | "IN_PROGRESS" | "RESOLVED" | "CLOSED";
  foto_bukti_url?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type PengaduanHistoryDto = {
  status_from?: string | null;
  status_to: string;
  notes?: string | null;
  created_at: string;
  changed_by?: string | null;
};

export type PengaduanDetailDto = PengaduanDto & {
  histori_tindak_lanjut?: PengaduanHistoryDto[];
};

export type DashboardSummaryDto = {
  total_pengajuan_surat_hari_ini: number;
  surat_pending: number;
  surat_verified: number;
  surat_processed: number;
  surat_done: number;
  surat_rejected: number;
  pengaduan_aktif: number;
  pengaduan_selesai: number;
  total_warga_aktif: number;
  total_unit_published: number;
};

export type DashboardAlertDto = {
  key: string;
  message: string;
  severity: "info" | "warning" | "critical";
  metric: number;
};

export type DashboardChartItemDto = {
  label: string;
  total: number;
};

export type DashboardTrendPointDto = {
  date: string;
  total: number;
};

export type DashboardHealthFlagDto = {
  key: string;
  label: string;
  total: number;
  severity: string;
  detail?: string | null;
};

export type DashboardQuickActionDto = {
  key: string;
  label: string;
  route_name: string;
  path: string;
  badge_count: number;
  category: string;
};

export type DashboardOverviewDto = {
  summary: DashboardSummaryDto;
  alerts: DashboardAlertDto[];
  charts: {
    surat_by_status: DashboardChartItemDto[];
    pengaduan_by_kategori: DashboardChartItemDto[];
    surat_trend: DashboardTrendPointDto[];
    pengaduan_trend: DashboardTrendPointDto[];
  };
  health: {
    content_flags: DashboardHealthFlagDto[];
    master_flags: DashboardHealthFlagDto[];
  };
  quick_actions: DashboardQuickActionDto[];
};

export type DashboardQueueItemDto = {
  id: string;
  module: string;
  title: string;
  subject_name: string;
  status: string;
  created_at: string;
  updated_at: string;
  age_hours: number;
  aging_bucket: string;
  attention_needed: boolean;
  detail_url: string;
};

export type DashboardQueueDto = {
  data: DashboardQueueItemDto[];
  meta: {
    scope: string;
    status?: string | null;
    aging?: string | null;
    total: number;
  };
};

export type DashboardActivityItemDto = {
  module: string;
  action: string;
  title: string;
  actor_name?: string | null;
  created_at: string;
  target_id: string;
  target_url: string;
};

export type DashboardActivityDto = {
  data: DashboardActivityItemDto[];
  meta: {
    limit: number;
    returned: number;
  };
};

export type DashboardAnalyticsDto = {
  data: Record<string, unknown>;
};

export type DashboardHealthDto = {
  data: Record<string, unknown>;
};
