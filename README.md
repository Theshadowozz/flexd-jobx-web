# flexd-jobx-web

Monorepo backend FastAPI/MySQL dan frontend React/TypeScript. Dependensi dan proses terpisah.

## Setup backend

Prasyarat: Python 3.11+, uv, MySQL 8 dengan schema existing.

1. Salin `backend/.env.example` ke `backend/.env`.
2. Isi konfigurasi `DB_*` dan `JWT_SECRET_KEY`. Secret JWT minimal 32 byte acak.
3. Jalankan dari `backend/`:

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Dokumentasi API: <http://127.0.0.1:8000/docs>.

`DB_SSL_DISABLED=true` secara eksplisit menonaktifkan TLS untuk development sesuai keputusan
proyek. Koneksi tidak terenkripsi; batasi firewall ke IP aplikasi. Untuk TLS tervalidasi, set
`DB_SSL_DISABLED=false`, dengan `DB_SSL_CA` opsional untuk CA privat.

Aplikasi tidak membuat atau mengubah schema saat startup. Endpoint health/readiness dihapus.
Kredensial asli tidak disertakan; `.env` diabaikan Git.

## Provisioning admin pertama

Operator menjalankan dari `backend/`:

```bash
uv run python -m scripts.provision_admin --email admin@example.com --name Admin
```

Command meminta password dan konfirmasi target sebelum menulis. Tidak dijalankan otomatis.
Jika admin sudah ada, gunakan pengelolaan akun terautentikasi. Jangan menjalankan command ini
pada DB remote tanpa persetujuan operator. Password baru memakai Argon2id; format hash legacy
yang belum dikenali tidak dapat login sampai tersedia migrasi/reset terkontrol.

## Auth dan CRUD

```text
POST  /api/v1/auth/login
GET   /api/v1/auth/me
PATCH /api/v1/auth/password
```

Login menerima JSON `email`/`password`; response berisi `data.access_token`, `token_type`,
`expires_in`, dan `user`. Kirim `Authorization: Bearer <token>` untuk request terproteksi.
Ganti password menerima `current_password`/`new_password`.

CRUD seluruh resource **admin-only**, akun harus aktif:

| Resource | Key single | Key list |
|---|---|---|
| users | user | users |
| candidate-profiles | candidate_profile | candidate_profiles |
| company-profiles | company_profile | company_profiles |
| skills | skill | skills |
| skill-aliases | skill_alias | skill_aliases |
| artifacts | artifact | artifacts |
| artifact-analyses | artifact_analysis | artifact_analyses |
| artifact-contributions | artifact_contribution | artifact_contributions |
| artifact-skill-evidences | artifact_skill_evidence | artifact_skill_evidences |
| job-posts | job_post | job_posts |
| job-skill-requirements | job_skill_requirement | job_skill_requirements |
| job-matches | job_match | job_matches |

Setiap resource: `POST`/`GET /api/v1/<resource>` dan `GET`/`PATCH`/`DELETE
`/api/v1/<resource>/{record_id}`. Profil kandidat memakai `{user_id}`.
Create `201`; read/update/delete `200`. Pagination `offset=0`, `limit=20`, maksimum 100.
Filter typed tersedia dalam OpenAPI. Urutan berdasarkan primary key.

```json
{
  "message": {"success": "Alias skill berhasil diambil"},
  "error": {},
  "data": {
    "skill_alias": {"id": 10, "skill_id": 1, "alias_name": "ReactJS", "normalized_alias": "reactjs"}
  }
}
```

List memakai key jamak dan `data.pagination` berisi `offset`, `limit`, `total`.
Delete sukses memakai `data: {}`.

```json
{
  "message": {"error": "Validasi gagal"},
  "error": {"validation": {"alias_name": "Field wajib diisi"}},
  "data": {}
}
```

Error kategori: `bad_request` (400), `authentication` (401), `authorization` (403),
`not_found` (404), `method_not_allowed` (405), `conflict`/`business_rule` (409),
`validation` (422), `rate_limit` (429), `internal` (500), `service_unavailable` (503).
Handler HTTP juga mengenali 413/415/502/504. Format custom JobX, bukan RFC 9457.
SQL, input sensitif, dan stack trace tidak dikirim ke client.

PATCH menolak body kosong dan field asing. Hanya field terkirim diubah. Field relasi utama,
primary key, dan timestamp server tidak dapat dipindahkan lewat PATCH. Null untuk kolom wajib
ditolak oleh service. Field JSON diganti seluruhnya; null mengosongkan kolom nullable.

ID tetap angka JSON. Nilai di atas `Number.MAX_SAFE_INTEGER` memerlukan parser lossless pada
client JavaScript; migrasi kontrak ID ke string belum diterapkan. Decimal diserialisasi string.
Timestamp DB berupa DATETIME tanpa zona; timestamp tindakan baru menggunakan UTC tanpa offset.
Zona data legacy belum diverifikasi.

## Aturan dan batas keamanan

- Password hash tidak masuk response. Role/status hanya admin. Admin aktif terakhir dilindungi.
- Role profil/pemilik lowongan/kandidat matching diperiksa.
- Skill parent tidak boleh siklik; evidence harus memakai analysis dari artifact yang sama.
- Rentang gaji/tanggal diperiksa terhadap keadaan akhir PATCH.
- Publish mensyaratkan approval approved. Status matching diturunkan dari keputusan pihak terkait;
  expired tetap tindakan eksplisit. Tidak ada scheduler penutupan/expiry.
- Delete permanen mengikuti FK existing. Artifact menghapus analysis/contribution/evidence;
  lowongan menghapus requirement/match. User pemilik lowongan dan skill yang dipakai requirement/
  evidence dapat ditolak dihapus. Penghapusan DB tidak menghapus object S3.
- Login rate limit 10 request/menit/IP **per proses**. Deployment beberapa worker memerlukan
  pembatasan bersama di gateway. Jangan mempercayai forwarded client IP dari proxy tak tepercaya.
- JWT memvalidasi signature, algorithm, issuer, audience, subject, iat, exp. Akun inactive ditolak.
- Password change tidak mencabut token existing. Tidak ada refresh token/revocation/logout palsu.
- Output analysis mentah hanya tersedia melalui CRUD admin; jangan membuka endpoint ini ke publik.

## Arsitektur backend

`routes` mendaftarkan HTTP dan izin; `controllers` membentuk response; `services` menjalankan
query/transaksi/aturan; `models` mapping tabel; `schemas` whitelist input/output.
Dependency akses di `configs/dependencies.py`; handler exception di `utils/exceptions.py`.
Query, transaksi, dan validasi berada langsung di service masing-masing resource.
Pembentukan response berada di controller; registrasi endpoint berada di route masing-masing.
Route memakai decorator dan `Depends`, `Path`, serta `Query` langsung, tanpa `Annotated`.
Setiap service/controller memiliki fungsi bernama entity: create, list, get, update, delete.
Create dan update mempunyai implementasi terpisah, assignment field eksplisit, serta transaksi
masing-masing. Tidak memakai `_write`, introspeksi kolom, atau loop `setattr` untuk CRUD.
Tidak ada repository layer atau SQL dinamis dari nama tabel client.

## Frontend

Prasyarat Node.js 22.12+; jalankan dari `frontend/`:

```bash
npm ci
npm run dev
```

Frontend mempertahankan React, Redux Toolkit, Tailwind, shadcn/ui, react-hook-form, dan Zod.
Form health dihapus. Home hanya placeholder; UI login/admin belum dibuat.
API client umum di `src/lib/api.ts` membaca error berkategori.
Development proxy `/api` ke backend. `VITE_APP_API_BASE_URL` opsional dan publik; jangan isi secret.

## Pengujian

Dari `backend/`:

```bash
uv run python -m unittest discover -s tests -v
uv run ruff check app tests scripts
```

Functional test memakai SQLite in-memory, bukan DB remote. Test mencakup CRUD 12 resource,
auth, whitelist field, validasi relasi/status, rollback, serta response.
SQLite tidak membuktikan collation, unsigned bigint, row locking, atau timestamp MySQL.

Test MySQL opt-in melalui `DB_TEST_URL` dengan driver `mysql+pymysql`, schema terpisah berakhiran
`_test`, dan schema sudah disiapkan operator. Test menolak host aplikasi remote dan tidak
menjalankan DDL; perubahan dibungkus transaksi rollback. Test MySQL saat ini mencakup skill/alias;
pengujian lengkap 12 tabel dan concurrency MySQL masih perlu dilengkapi/diverifikasi.

Dari `frontend/`:

```bash
npm test
npm run lint
npm run build
```

## Di luar cakupan

Upload/delete S3, fetch URL, workflow LLM, perhitungan matching, audit log persisten,
akses ownership candidate/employer, dan UI pengelolaan belum dibuat. LangChain/LangGraph tetap
terpasang. Integrasi model direncanakan satu OpenAI-compatible, tanpa pilihan provider.
