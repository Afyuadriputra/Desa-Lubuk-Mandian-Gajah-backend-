# Ringkasan Hasil Unit Test

## Ringkasan Umum

- Total test dijalankan: **107**
- Total test berhasil: **107**
- Total test gagal: **0**
- Total test error: **0**
- Total test skipped: **0**

## Daftar Test yang Berhasil

### Auth Warga

- `features/auth_warga/tests/test_permissions.py::TestUserManagementPermissions::test_should_allow_superadmin_to_manage_admin_accounts`
- `features/auth_warga/tests/test_permissions.py::TestUserManagementPermissions::test_should_prevent_admin_from_managing_other_admin_accounts`
- `features/auth_warga/tests/test_permissions.py::TestUserManagementPermissions::test_should_allow_admin_to_manage_warga_accounts`
- `features/auth_warga/tests/test_permissions.py::TestSelfPermissions::test_should_allow_user_to_view_own_account`
- `features/auth_warga/tests/test_permissions.py::TestSelfPermissions::test_should_prevent_user_from_deactivating_self`
- `features/auth_warga/tests/test_permissions.py::TestUserCreationPermissions::test_should_allow_superadmin_to_create_admin_user`
- `features/auth_warga/tests/test_permissions.py::TestUserCreationPermissions::test_should_prevent_admin_from_creating_admin_user`
- `features/auth_warga/tests/test_permissions.py::TestUserCreationPermissions::test_should_allow_admin_to_create_warga_user`
- `features/auth_warga/tests/test_permissions.py::TestUserCreationPermissions::test_should_prevent_warga_from_creating_warga_user`
- `features/auth_warga/tests/test_services.py::TestLoginService::test_should_login_successfully_with_valid_credentials`
- `features/auth_warga/tests/test_services.py::TestLoginService::test_should_fail_login_when_password_is_wrong`
- `features/auth_warga/tests/test_services.py::TestLoginService::test_should_fail_login_when_account_is_inactive`
- `features/auth_warga/tests/test_services.py::TestLoginService::test_should_fail_login_when_nik_is_invalid`
- `features/auth_warga/tests/test_services.py::TestLoginService::test_should_fail_login_when_user_not_found`
- `features/auth_warga/tests/test_services.py::TestAccountActivationService::test_should_allow_admin_to_deactivate_warga_account`
- `features/auth_warga/tests/test_services.py::TestAccountActivationService::test_should_allow_admin_to_activate_warga_account`
- `features/auth_warga/tests/test_services.py::TestAccountActivationService::test_should_prevent_admin_from_deactivating_self`
- `features/auth_warga/tests/test_services.py::TestAccountActivationService::test_should_raise_error_when_target_user_not_found`
- `features/auth_warga/tests/test_services.py::TestAccountActivationService::test_should_prevent_admin_from_managing_other_admin_accounts`
- `features/auth_warga/tests/test_services.py::TestWargaAccountCreationService::test_should_allow_admin_to_create_warga_account`
- `features/auth_warga/tests/test_services.py::TestWargaAccountCreationService::test_should_prevent_warga_from_creating_warga_account`
- `features/auth_warga/tests/test_services.py::TestWargaAccountCreationService::test_should_reject_duplicate_nik_when_creating_warga`
- `features/auth_warga/tests/test_services.py::TestAdminAccountCreationService::test_should_allow_superadmin_to_create_admin_account`
- `features/auth_warga/tests/test_services.py::TestAdminAccountCreationService::test_should_allow_superadmin_to_create_bumdes_account`
- `features/auth_warga/tests/test_services.py::TestAdminAccountCreationService::test_should_prevent_admin_from_creating_admin_account`
- `features/auth_warga/tests/test_services.py::TestAdminAccountCreationService::test_should_reject_invalid_role_when_creating_admin`
- `features/auth_warga/tests/test_services.py::TestAdminAccountCreationService::test_should_reject_warga_role_when_creating_admin`
- `features/auth_warga/tests/test_views.py::TestLoginView::test_should_return_200_when_login_successful`
- `features/auth_warga/tests/test_views.py::TestLoginView::test_should_return_400_when_payload_invalid`
- `features/auth_warga/tests/test_views.py::TestLoginView::test_should_return_400_when_required_fields_missing`
- `features/auth_warga/tests/test_views.py::TestLoginView::test_should_return_400_when_nik_invalid`
- `features/auth_warga/tests/test_views.py::TestLoginView::test_should_return_403_when_account_inactive`
- `features/auth_warga/tests/test_views.py::TestLoginView::test_should_return_401_when_password_wrong`
- `features/auth_warga/tests/test_views.py::TestMeView::test_should_return_401_when_not_authenticated`
- `features/auth_warga/tests/test_views.py::TestMeView::test_should_return_user_data_when_authenticated`
- `features/auth_warga/tests/test_views.py::TestCreateWargaUserView::test_should_return_401_when_not_authenticated`
- `features/auth_warga/tests/test_views.py::TestCreateWargaUserView::test_should_allow_admin_to_create_warga`
- `features/auth_warga/tests/test_views.py::TestCreateWargaUserView::test_should_return_400_when_nik_duplicate`
- `features/auth_warga/tests/test_views.py::TestCreateWargaUserView::test_should_return_403_when_warga_create_warga`
- `features/auth_warga/tests/test_views.py::TestCreateAdminUserView::test_should_return_401_when_not_authenticated`
- `features/auth_warga/tests/test_views.py::TestCreateAdminUserView::test_should_allow_superadmin_to_create_admin`
- `features/auth_warga/tests/test_views.py::TestCreateAdminUserView::test_should_return_403_when_admin_create_admin`
- `features/auth_warga/tests/test_views.py::TestCreateAdminUserView::test_should_return_400_when_role_invalid`
- `features/auth_warga/tests/test_views.py::TestCreateAdminUserView::test_should_return_400_when_role_is_warga`
- `features/auth_warga/tests/test_views.py::TestActivationView::test_should_return_403_when_user_has_no_permission`
- `features/auth_warga/tests/test_views.py::TestActivationView::test_should_allow_admin_to_activate_warga`
- `features/auth_warga/tests/test_views.py::TestActivationView::test_should_return_404_when_deactivate_user_not_found`
- `features/auth_warga/tests/test_domain.py::TestNormalizeNIK::test_should_remove_non_digit_characters_from_nik`
- `features/auth_warga/tests/test_domain.py::TestValidateNIK::test_should_pass_when_nik_is_valid_16_digits`
- `features/auth_warga/tests/test_domain.py::TestValidateNIK::test_should_raise_error_when_nik_length_is_invalid`
- `features/auth_warga/tests/test_domain.py::TestAccountStatus::test_should_raise_error_when_account_is_inactive`
- `features/auth_warga/tests/test_domain.py::TestValidateRole::test_should_pass_for_all_valid_roles`
- `features/auth_warga/tests/test_domain.py::TestValidateRole::test_should_raise_error_for_invalid_role`
- `features/auth_warga/tests/test_domain.py::TestInternalAdminRole::test_should_return_true_for_internal_admin_roles`
- `features/auth_warga/tests/test_domain.py::TestInternalAdminRole::test_should_return_false_for_warga_role`

### Layanan Administrasi

- `features/layanan_administrasi/tests/test_integration.py::TestSuratEndToEnd::test_should_complete_full_flow_from_submit_to_done`
- `features/layanan_administrasi/tests/test_repositories.py::TestCreateSuratRepository::test_should_create_surat_and_initial_history`
- `features/layanan_administrasi/tests/test_repositories.py::TestUpdateStatusRepository::test_should_update_status_and_create_history`
- `features/layanan_administrasi/tests/test_repositories.py::TestUpdateStatusRepository::test_should_store_nomor_surat_when_provided`
- `features/layanan_administrasi/tests/test_repositories.py::TestUpdateStatusRepository::test_should_store_rejection_reason_when_rejected`
- `features/layanan_administrasi/tests/test_repositories.py::TestUpdateStatusRepository::test_should_not_set_rejection_reason_if_not_rejected`
- `features/layanan_administrasi/tests/test_services.py::TestProsesSuratAdvanced::test_should_follow_valid_state_machine_flow`
- `features/layanan_administrasi/tests/test_services.py::TestProsesSuratAdvanced::test_should_reject_invalid_transition`
- `features/layanan_administrasi/tests/test_services.py::TestProsesSuratAdvanced::test_should_require_rejection_reason`
- `features/layanan_administrasi/tests/test_services.py::TestProsesSuratAdvanced::test_should_allow_rejection_with_reason`
- `features/layanan_administrasi/tests/test_services.py::TestNomorSurat::test_should_generate_nomor_surat_if_not_provided`
- `features/layanan_administrasi/tests/test_services.py::TestNomorSurat::test_should_not_override_manual_nomor`
- `features/layanan_administrasi/tests/test_services.py::TestPDFGeneration::test_should_attach_pdf_when_done`
- `features/layanan_administrasi/tests/test_services.py::TestPDFGeneration::test_should_not_crash_when_pdf_fails`
- `features/layanan_administrasi/tests/test_services.py::TestAuditLogging::test_should_log_event_when_submit`
- `features/layanan_administrasi/tests/test_services.py::TestDataConsistency::test_status_should_match_latest_history`
- `features/layanan_administrasi/tests/test_views.py::TestAjukanSuratView::test_should_return_401_when_not_authenticated`
- `features/layanan_administrasi/tests/test_views.py::TestAjukanSuratView::test_should_allow_warga_submit`
- `features/layanan_administrasi/tests/test_views.py::TestAjukanSuratView::test_admin_cannot_submit_surat`
- `features/layanan_administrasi/tests/test_views.py::TestAjukanSuratView::test_invalid_payload_should_fail`
- `features/layanan_administrasi/tests/test_views.py::TestListSuratView::test_should_return_401_when_not_authenticated`
- `features/layanan_administrasi/tests/test_views.py::TestDetailSuratView::test_warga_cannot_view_other_user_surat`
- `features/layanan_administrasi/tests/test_views.py::TestListSuratAdvanced::test_warga_only_see_own_surat`
- `features/layanan_administrasi/tests/test_views.py::TestListSuratAdvanced::test_admin_can_see_all_surat`
- `features/layanan_administrasi/tests/test_views.py::TestDetailSuratEdgeCase::test_should_return_404_if_surat_not_found`
- `features/layanan_administrasi/tests/test_views.py::TestDetailSuratSuccess::test_warga_can_view_own_surat`
- `features/layanan_administrasi/tests/test_views.py::TestDetailSuratAdmin::test_admin_can_view_any_surat`
- `features/layanan_administrasi/tests/test_views.py::TestListSuratEmpty::test_should_return_empty_list`
- `features/layanan_administrasi/tests/test_views.py::TestAjukanSuratValidationEdge::test_missing_keperluan_should_fail`
- `features/layanan_administrasi/tests/test_domain.py::TestJenisSuratValidation::test_should_accept_valid_jenis_surat`
- `features/layanan_administrasi/tests/test_domain.py::TestJenisSuratValidation::test_should_reject_invalid_jenis_surat`
- `features/layanan_administrasi/tests/test_domain.py::TestKeperluanValidation::test_should_reject_empty_keperluan`
- `features/layanan_administrasi/tests/test_domain.py::TestKeperluanValidation::test_should_reject_short_keperluan`
- `features/layanan_administrasi/tests/test_domain.py::TestKeperluanValidation::test_should_accept_valid_keperluan`
- `features/layanan_administrasi/tests/test_domain.py::TestStatusTransition::test_should_allow_valid_transition`
- `features/layanan_administrasi/tests/test_domain.py::TestStatusTransition::test_should_reject_invalid_transition`
- `features/layanan_administrasi/tests/test_domain.py::TestRejectionValidation::test_should_require_reason_when_rejected`
- `features/layanan_administrasi/tests/test_domain.py::TestRejectionValidation::test_should_pass_when_reason_provided`

### Pengaduan Warga

- `features/pengaduan_warga/tests/test_repositories.py::TestPengaduanRepository::test_create_dan_update_status_mencatat_histori_db`
- `features/pengaduan_warga/tests/test_views.py::TestPengaduanAPI::test_list_pengaduan_tanpa_login_ditolak`
- `features/pengaduan_warga/tests/test_views.py::TestPengaduanAPI::test_buat_pengaduan_payload_tidak_valid`
- `features/pengaduan_warga/tests/test_views.py::TestPengaduanAPI::test_warga_tidak_bisa_lihat_pengaduan_warga_lain`
- `features/pengaduan_warga/tests/test_domain.py::TestDomainPengaduan::test_validasi_input_berhasil`
- `features/pengaduan_warga/tests/test_domain.py::TestDomainPengaduan::test_validasi_input_judul_terlalu_pendek`
- `features/pengaduan_warga/tests/test_domain.py::TestDomainPengaduan::test_transisi_status_valid`
- `features/pengaduan_warga/tests/test_domain.py::TestDomainPengaduan::test_transisi_status_invalid`
- `features/pengaduan_warga/tests/test_domain.py::TestDomainPengaduan::test_catatan_wajib_saat_resolved`
- `features/pengaduan_warga/tests/test_services.py::TestPengaduanService::test_warga_bisa_buat_pengaduan`
- `features/pengaduan_warga/tests/test_services.py::TestPengaduanService::test_admin_tidak_bisa_buat_pengaduan`
- `features/pengaduan_warga/tests/test_services.py::TestPengaduanService::test_warga_tidak_bisa_lihat_pengaduan_warga_lain`
- `features/pengaduan_warga/tests/test_services.py::TestPengaduanService::test_upload_file_melebihi_batas_ditolak`
- `features/pengaduan_warga/tests/test_services.py::TestPengaduanService::test_audit_dan_history_dipanggil_saat_proses`

## Use Case yang Diuji

### Auth Warga

- Allow superadmin to manage admin accounts
- Prevent admin from managing other admin accounts
- Allow admin to manage warga accounts
- Allow user to view own account
- Prevent user from deactivating self
- Allow superadmin to create admin user
- Prevent admin from creating admin user
- Allow admin to create warga user
- Prevent warga from creating warga user
- Login successfully with valid credentials
- Fail login when password is wrong
- Fail login when account is inactive
- Fail login when nik is invalid
- Fail login when user not found
- Allow admin to deactivate warga account
- Allow admin to activate warga account
- Prevent admin from deactivating self
- Raise error when target user not found
- Allow admin to create warga account
- Prevent warga from creating warga account
- Reject duplicate nik when creating warga
- Allow superadmin to create admin account
- Allow superadmin to create bumdes account
- Prevent admin from creating admin account
- Reject invalid role when creating admin
- Reject warga role when creating admin
- Return 200 when login successful
- Return 400 when payload invalid
- Return 400 when required fields missing
- Return 400 when nik invalid
- Return 403 when account inactive
- Return 401 when password wrong
- Return 401 when not authenticated
- Return user data when authenticated
- Allow admin to create warga
- Return 400 when nik duplicate
- Return 403 when warga create warga
- Allow superadmin to create admin
- Return 403 when admin create admin
- Return 400 when role invalid
- Return 400 when role is warga
- Return 403 when user has no permission
- Allow admin to activate warga
- Return 404 when deactivate user not found
- Remove non digit characters from nik
- Pass when nik is valid 16 digits
- Raise error when nik length is invalid
- Raise error when account is inactive
- Pass for all valid roles
- Raise error for invalid role
- Return true for internal admin roles
- Return false for warga role

### Layanan Administrasi

- Complete full flow from submit to done
- Create surat and initial history
- Update status and create history
- Store nomor surat when provided
- Store rejection reason when rejected
- Not set rejection reason if not rejected
- Follow valid state machine flow
- Reject invalid transition
- Require rejection reason
- Allow rejection with reason
- Generate nomor surat if not provided
- Not override manual nomor
- Attach pdf when done
- Not crash when pdf fails
- Log event when submit
- Status should match lahistory
- Return 401 when not authenticated
- Allow warga submit
- Admin cannot submit surat
- Invalid payload should fail
- Warga cannot view other user surat
- Warga only see own surat
- Admin can see all surat
- Return 404 if surat not found
- Warga can view own surat
- Admin can view any surat
- Return empty list
- Missing keperluan should fail
- Accept valid jenis surat
- Reject invalid jenis surat
- Reject empty keperluan
- Reject short keperluan
- Accept valid keperluan
- Allow valid transition
- Require reason when rejected
- Pass when reason provided

### Pengaduan Warga

- Create dan update status mencatat histori db
- List pengaduan tanpa login ditolak
- Buat pengaduan payload tidak valid
- Warga tidak bisa lihat pengaduan warga lain
- Validasi input berhasil
- Validasi input judul terlalu pendek
- Transisi status valid
- Transisi status invalid
- Catatan wajib saat resolved
- Warga bisa buat pengaduan
- Admin tidak bisa buat pengaduan
- Upload file melebihi batas ditolak
- Audit dan history dipanggil saat proses
