---
title: "Product Requirements Document (PRD) — JobX"
version: "1.0"
date: "14 November 2026"
language: "Bahasa Indonesia"
status: "Baseline kebutuhan MVP untuk pengembangan hackathon"
---

**PRODUCT REQUIREMENTS  
DOCUMENT**

**JOBX**

Platform Pencarian Kerja Berbasis AI dan Bukti Kompetensi

> **POSITIONING PRODUK**  
> JobX menghubungkan pencari kerja dan pemberi kerja melalui analisis artifact, pemetaan keterampilan berbasis bukti, pembuatan deskripsi pekerjaan dari kebutuhan bisnis, dan pencocokan yang dapat dijelaskan.

**Versi 1.0 \| 14 November 2026**

Dokumen kebutuhan produk untuk pengembangan MVP Hackathon

# Informasi Dokumen

| **Atribut**     | **Keterangan**                                                 |
|-----------------|----------------------------------------------------------------|
| Nama produk     | JobX                                                           |
| Nama dokumen    | Product Requirements Document (PRD)                            |
| Versi           | 1.0                                                            |
| Tanggal         | 14 November 2026                                               |
| Status          | Baseline kebutuhan MVP untuk pengembangan hackathon            |
| Bahasa          | Bahasa Indonesia                                               |
| Pemilik dokumen | Tim JobX (nama penanggung jawab belum ditetapkan dalam sumber) |
| Basis rancangan | Konsep ide JobX dan skema MySQL JobX versi kompatibel terbaru  |

## Riwayat Versi

| **Versi** | **Tanggal**      | **Perubahan**                                                                                                                            |
|-----------|------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| 1.0       | 14 November 2026 | Penyusunan PRD awal; memasukkan empat fitur inti dan integrasi GitHub OAuth untuk pemilihan repository publik tanpa tabel database baru. |

## Cara Membaca Dokumen

Dokumen ini menjelaskan kebutuhan produk, alur pengguna, aturan bisnis, kebutuhan sistem, serta kriteria penerimaan JobX. Kebutuhan yang berasal langsung dari konsep awal dipertahankan sebagai arah produk. Rekomendasi tambahan untuk membatasi ruang lingkup, mengelola risiko, dan mempersiapkan implementasi MVP diberi penanda sebagai keputusan desain atau rekomendasi yang masih dapat disesuaikan.

Istilah “harus” menyatakan persyaratan yang wajib dipenuhi pada ruang lingkup MVP. Istilah “sebaiknya” menyatakan rekomendasi desain. Target angka yang belum memiliki baseline empiris ditandai sebagai target awal yang perlu divalidasi melalui pengujian.

# Daftar Isi

- 1\. Ringkasan Produk dan Visi

- 2\. Latar Belakang, Masalah, dan Peluang

- 3\. Tujuan Produk dan Indikator Keberhasilan

- 4\. Pengguna Sasaran dan Persona

- 5\. Ruang Lingkup Produk

- 6\. Perjalanan Pengguna dan Alur Utama

- 7\. Kebutuhan Fungsional

- 8\. Persyaratan Sistem AI

- 9\. Aturan Bisnis dan Logika Pencocokan

- 10\. Persyaratan Nonfungsional

- 11\. Persyaratan Data dan Basis Data

- 12\. Arsitektur Teknis dan Integrasi

- 13\. Kriteria Penerimaan dan Strategi Pengujian

- 14\. Tahapan Implementasi, Risiko, dan Asumsi

- 15\. Glosarium dan Referensi

# 1. Ringkasan Produk dan Visi

## 1.1 Gambaran Umum

JobX adalah platform pencarian dan pencocokan pekerjaan berbasis kecerdasan buatan yang menghubungkan pencari kerja (job seeker/candidate) dengan pemberi kerja (employer). Konsep awal JobX digambarkan sebagai penggabungan karakteristik jejaring profesional seperti LinkedIn dengan mekanisme pilihan dua arah seperti Tinder. Mekanisme tersebut digunakan untuk menyederhanakan proses penemuan peluang dan penyampaian ketertarikan, bukan untuk menggantikan proses seleksi profesional.

Pembeda utama JobX adalah penggunaan artifact, yaitu hasil pekerjaan atau project yang pernah dibuat kandidat, sebagai sumber bukti awal untuk mengidentifikasi keterampilan. Artifact dapat berupa repository GitHub, dokumen, spreadsheet, gambar, video, atau tautan karya lain sesuai dukungan format pada tahap implementasi. Kandidat juga menjelaskan peran dan kontribusinya agar analisis AI tidak menganggap seluruh isi project sebagai hasil kerja pribadi kandidat.

Dari sisi employer, JobX menerima deskripsi permasalahan bisnis atau kebutuhan pekerjaan. Sistem membantu menerjemahkan masukan tersebut menjadi deskripsi pekerjaan yang terstruktur, termasuk tanggung jawab dan keterampilan yang dibutuhkan. Selanjutnya, matching engine membandingkan kebutuhan pekerjaan dengan keterampilan dan evidence kandidat, menghasilkan rekomendasi beserta alasan yang dapat diperiksa.

## 1.2 Visi Produk

> **VISI JOBX**  
> Membantu proses rekrutmen menjadi lebih relevan dan berbasis bukti dengan menghubungkan kebutuhan pekerjaan dan kompetensi kandidat melalui artifact, analisis AI, serta pencocokan yang transparan.

## 1.3 Prinsip Produk

- **Berbasis bukti.** Keterampilan kandidat ditampilkan bersama sumber evidence dari artifact, bukan hanya sebagai klaim tanpa konteks.

- **Dapat dijelaskan.** Rekomendasi pekerjaan atau kandidat harus menyertakan alasan dan komponen kecocokan yang dapat dipahami pengguna.

- **Human-in-the-loop.** AI membantu analisis dan rekomendasi; kandidat dapat meninjau hasil ekstraksi dan employer tetap mengambil keputusan rekrutmen.

- **Berorientasi privasi.** Pengguna mengendalikan artifact yang dibagikan dan sistem hanya meminta akses yang diperlukan.

- **Terfokus pada MVP.** Implementasi hackathon memprioritaskan alur artifact hingga matching yang dapat didemonstrasikan secara menyeluruh.

## 1.4 Definisi Nilai Produk

| **Pengguna**  | **Nilai yang ditawarkan JobX**                                                                                                                                 |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Job seeker    | Memperlihatkan kemampuan melalui hasil pekerjaan; memperoleh rekomendasi lowongan yang lebih relevan; mengurangi ketergantungan pada CV dan kata kunci semata. |
| Employer      | Menerjemahkan kebutuhan bisnis menjadi kualifikasi yang terstruktur; melihat bukti yang relevan pada artifact; mempercepat penyaringan awal kandidat.          |
| Tim rekrutmen | Mendapatkan struktur informasi yang lebih konsisten untuk meninjau kecocokan kandidat dan mendokumentasikan alasan rekomendasi.                                |

# 2. Latar Belakang, Masalah, dan Peluang

## 2.1 Rumusan Masalah dari Konsep Awal

Konsep awal JobX mengidentifikasi dua kelompok persoalan. Pertama, persaingan pencarian kerja membuat kandidat sulit menemukan pekerjaan yang benar-benar sesuai dengan keterampilannya. Kedua, employer menghadapi beban penyaringan ketika menerima banyak lamaran, termasuk lamaran yang tidak relevan dengan kebutuhan posisi. CV dan pernyataan keterampilan juga belum tentu menunjukkan bagaimana kandidat menerapkan keterampilan tersebut dalam pekerjaan nyata.

Konsep awal juga mengangkat referral atau rekomendasi personal sebagai salah satu kanal yang dianggap berpengaruh dalam penerimaan kandidat. Dalam PRD ini, isu tersebut diperlakukan sebagai hipotesis masalah yang perlu diuji, bukan fakta bahwa mayoritas kandidat diterima melalui “orang dalam”. Data nasional yang sebanding mengenai rasio penerimaan melalui referral dibandingkan aplikasi online belum ditetapkan dalam basis bukti dokumen ini.

## 2.2 Indikator Pasar Kerja Indonesia

Data pasar kerja berikut digunakan untuk menggambarkan konteks kebutuhan pencarian kerja dan kompetisi pasar. Data ini tidak dengan sendirinya membuktikan bahwa teknologi rekrutmen tertentu akan menyelesaikan pengangguran atau meningkatkan tingkat penerimaan kandidat.

| **Indikator**                                          | **Nilai**         | **Periode / penjelasan**                               |
|--------------------------------------------------------|-------------------|--------------------------------------------------------|
| Pencari kerja aktif di Karirhub                        | 892.306 orang     | Status aktif per 1 Oktober 2026.                       |
| Lowongan melalui Karirhub dan JOSS                     | 106.776 lowongan  | Januari–Oktober 2026.                                  |
| Kebutuhan tenaga kerja pada lowongan Karirhub dan JOSS | 384.642 orang     | Januari–September 2026.                                |
| Lamaran kerja di Karirhub                              | 3.518.046 lamaran | Januari–September 2026.                                |
| Tingkat Pengangguran Terbuka lulusan SMK               | 8,63%             | Data BPS tahun 2025; tabel diperbarui 30 Januari 2026. |
| Tingkat Pengangguran Terbuka lulusan universitas       | 5,39%             | Data BPS tahun 2025; tabel diperbarui 30 Januari 2026. |

Sumber: Pusat Pasar Kerja/Kemnaker (Pasker ID) dan Badan Pusat Statistik (BPS) \[1\]\[2\]. Angka Pasker ID merupakan statistik pada platform Karirhub dan JOSS, bukan keseluruhan pasar kerja Indonesia. Periode penghitungan antarindikator juga tidak seluruhnya sama, sehingga angka tersebut tidak digunakan untuk membentuk rasio lamaran per lowongan dalam PRD ini.

## 2.3 Kesenjangan Informasi dalam Rekrutmen

- **Kesenjangan kandidat.** Kandidat dapat memiliki hasil project yang relevan, tetapi sulit menerjemahkannya menjadi daftar kompetensi yang mudah dipahami recruiter.

- **Kesenjangan employer.** Employer dapat mendeskripsikan kebutuhan dalam bahasa operasional atau permasalahan bisnis, tetapi belum tentu memiliki spesifikasi kompetensi yang rinci.

- **Kesenjangan bukti.** Daftar skill dalam CV tidak selalu disertai contoh penerapan, konteks project, peran individu, atau lokasi bukti.

- **Kesenjangan pencocokan.** Pencocokan berdasarkan kata kunci sederhana dapat mengabaikan hubungan makna antara pekerjaan yang pernah dilakukan dan kebutuhan pekerjaan baru.

## 2.4 Landasan Pendekatan

OECD menjelaskan pendekatan skills-first sebagai pendekatan yang memberi perhatian lebih besar pada keterampilan yang dapat ditunjukkan, di samping penggunaan gelar dan pengalaman sebagai proksi kompetensi. OECD juga mencatat bahwa asesmen terstruktur dan wawancara berbasis kompetensi merupakan beberapa cara untuk menilai keterampilan yang ditunjukkan. Pendekatan ini mendukung arah JobX, tetapi tidak berarti artifact digital saja cukup untuk memastikan kemampuan kerja seseorang \[3\].

Panduan Responsible AI in Recruitment dari Pemerintah Inggris menyoroti risiko bias, eksklusi digital, transparansi, serta kebutuhan mekanisme assurance pada sistem AI rekrutmen. Karena itu, JobX harus menempatkan AI sebagai alat bantu penilaian, menyediakan alasan rekomendasi, serta mempertahankan kewenangan keputusan pada manusia \[4\].

## 2.5 Hipotesis yang Perlu Divalidasi

| **ID** | **Hipotesis**                                                                       | **Cara validasi**                                                                        |
|--------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| H-01   | Kandidat kesulitan menunjukkan kompetensi melalui CV saja.                          | Wawancara kandidat; uji apakah artifact memberi konteks tambahan yang dianggap bernilai. |
| H-02   | Recruiter membutuhkan informasi bukti penerapan skill untuk screening awal.         | Wawancara HR/recruiter; bandingkan proses review CV dengan profil artifact JobX.         |
| H-03   | Employer dapat menjelaskan kebutuhan bisnis lebih mudah daripada menulis JD teknis. | Uji prototipe input business problem kepada hiring manager.                              |
| H-04   | Rekomendasi yang disertai evidence lebih berguna daripada skor tanpa penjelasan.    | Uji kegunaan terhadap recruiter dan kandidat.                                            |
| H-05   | Kandidat bersedia menghubungkan GitHub untuk mengimpor repository publik.           | Uji onboarding, tingkat penyelesaian OAuth, dan tingkat impor repository.                |

# 3. Tujuan Produk dan Indikator Keberhasilan

## 3.1 Tujuan Produk

- Menyediakan sarana bagi kandidat untuk mengelola artifact dan menjelaskan kontribusi pribadi pada project.

- Menghasilkan pemetaan keterampilan yang memiliki jejak evidence dari artifact.

- Membantu employer menyusun Job Description dan kebutuhan keterampilan dari permasalahan bisnis.

- Menghasilkan rekomendasi kandidat dan pekerjaan berdasarkan tingkat relevansi keterampilan, bukti, dan preferensi.

- Menyediakan mekanisme ketertarikan dua arah melalui keputusan menerima atau menolak rekomendasi.

## 3.2 Tujuan MVP Hackathon

| **Tujuan MVP**  | **Hasil yang harus dapat diperlihatkan**                                                                                           |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------|
| Alur kandidat   | Pengguna mendaftar, melengkapi profil, mengimpor setidaknya satu repository publik GitHub atau menambahkan artifact yang didukung. |
| Analisis AI     | JobX memproses artifact, mengidentifikasi keterampilan, dan menampilkan evidence yang dapat diperiksa.                             |
| Alur employer   | Employer membuat profil perusahaan, memasukkan business problem, meninjau JD, dan memublikasikan pekerjaan.                        |
| Matching        | Sistem menghasilkan kandidat yang relevan untuk lowongan dan lowongan yang relevan untuk kandidat dengan alasan pencocokan.        |
| Mutual interest | Kandidat dan employer dapat menerima atau menolak rekomendasi; status berubah sesuai keputusan kedua pihak.                        |

## 3.3 Indikator Keberhasilan Produk

Indikator berikut menjadi ukuran evaluasi MVP. Target numerik final perlu ditetapkan setelah tim memiliki data baseline dari pengujian, sehingga dokumen ini tidak menetapkan angka yang belum didukung pengukuran.

| **Indikator**                            | **Definisi / cara hitung**                                                                                              | **Sumber data**                      |
|------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| Tingkat penyelesaian onboarding kandidat | Kandidat yang menyelesaikan profil dan menambahkan minimal satu artifact dibandingkan kandidat yang memulai onboarding. | user, candidate_profile, artifact    |
| Keberhasilan impor GitHub                | Jumlah proses impor repository yang berhasil dibandingkan proses impor yang dimulai.                                    | Log backend / event integrasi        |
| Keberhasilan analisis artifact           | Analisis berstatus completed dibandingkan analisis valid yang diminta.                                                  | artifact, artifact_analysis          |
| Keterlacakan skill evidence              | Proporsi skill hasil analisis yang memiliki evidence excerpt atau evidence location.                                    | artifact_skill_evidence              |
| Kegunaan JD hasil AI                     | Penilaian employer terhadap kelengkapan dan relevansi JD sebelum dipublikasikan.                                        | Uji pengguna / survei                |
| Relevansi rekomendasi                    | Penilaian recruiter terhadap kesesuaian kandidat pada daftar rekomendasi.                                               | Uji pengguna / evaluasi dataset demo |
| Mutual acceptance rate                   | Pasangan job-candidate yang diterima kedua pihak dibandingkan pasangan yang memperoleh rekomendasi.                     | job_match                            |
| Waktu pembuatan JD                       | Durasi sejak employer mengirim business problem sampai draft JD siap ditinjau.                                          | Log aplikasi                         |

# 4. Pengguna Sasaran dan Persona

## 4.1 Kelompok Pengguna

| **Peran**              | **Deskripsi**                                                                                                                                                                                                     | **Kebutuhan utama**                                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Job seeker / Candidate | Individu yang mencari peluang kerja dan ingin menunjukkan kompetensi melalui hasil pekerjaan. MVP difokuskan pada bidang software engineering dan pekerjaan digital sebagai rekomendasi pembatasan ruang lingkup. | Mengelola profil, mengimpor artifact, menjelaskan kontribusi, memeriksa skill evidence, dan menemukan lowongan relevan. |
| Employer / Recruiter   | Pengguna yang mewakili perusahaan dan bertanggung jawab mendefinisikan kebutuhan posisi serta meninjau kandidat.                                                                                                  | Mengelola company profile, menyusun JD dari business problem, melihat bukti kandidat, serta menyampaikan keputusan.     |
| Administrator          | Pengelola operasional aplikasi dan data master untuk kebutuhan MVP.                                                                                                                                               | Mengelola akun/akses secara terbatas, master skill, dan penanganan masalah operasional.                                 |

## 4.2 Persona Kandidat

> **PERSONA A — KANDIDAT**  
> Profil ilustratif: mahasiswa tingkat akhir, lulusan baru, atau junior developer yang telah mengerjakan project individu/kelompok dan memiliki repository atau dokumen hasil pekerjaan. Persona ini mewakili kebutuhan untuk menerjemahkan pengalaman project menjadi bukti kompetensi yang mudah diperiksa.

- Tujuan: memperoleh pekerjaan yang sesuai dengan kemampuan dan preferensi kerja.

- Kendala: belum memiliki pengalaman kerja formal yang panjang; sulit menulis CV yang menjelaskan kontribusi teknis secara rinci.

- Perilaku yang diharapkan: menghubungkan GitHub, memilih repository, menjelaskan role, meninjau hasil analisis, dan menyatakan ketertarikan pada lowongan.

## 4.3 Persona Employer

> **PERSONA B — EMPLOYER / RECRUITER**  
> Profil ilustratif: recruiter atau hiring manager pada perusahaan rintisan/UKM teknologi yang memahami kebutuhan bisnis, tetapi ingin bantuan menyusun persyaratan teknis dan menyaring kandidat secara lebih konsisten.

- Tujuan: menemukan kandidat yang memiliki bukti keterampilan relevan untuk menyelesaikan kebutuhan pekerjaan.

- Kendala: menerima banyak lamaran dengan informasi kemampuan yang tidak seragam; sulit menilai kontribusi kandidat dari ringkasan CV saja.

- Perilaku yang diharapkan: menjelaskan business problem, memeriksa dan menyetujui JD, melihat kandidat yang direkomendasikan, serta menerima atau menolak kandidat.

## 4.4 Hak Akses berdasarkan Peran

| **Aktivitas**                       | **Candidate**                        | **Employer**                    | **Admin**                                    |
|-------------------------------------|--------------------------------------|---------------------------------|----------------------------------------------|
| Mengelola profil kandidat           | Ya                                   | Tidak                           | Terbatas                                     |
| Mengelola company profile           | Tidak                                | Ya                              | Terbatas                                     |
| Mengelola artifact sendiri          | Ya                                   | Tidak                           | Terbatas                                     |
| Mengelola lowongan sendiri          | Tidak                                | Ya                              | Terbatas                                     |
| Melihat hasil matching              | Untuk lowongan yang direkomendasikan | Untuk kandidat pada lowongannya | Sesuai kebutuhan operasional                 |
| Mengambil keputusan mutual interest | Keputusan kandidat                   | Keputusan employer              | Tidak mengambil keputusan atas nama pengguna |
| Mengelola master skill              | Tidak                                | Tidak                           | Ya                                           |

# 5. Ruang Lingkup Produk

## 5.1 Ruang Lingkup MVP

MVP berfokus pada pembuktian alur inti dari artifact menjadi skill evidence, dari business problem menjadi job requirement, lalu dari keduanya menjadi rekomendasi yang dapat dijelaskan dan diputuskan oleh dua pihak.

| **Modul**            | **Termasuk dalam MVP**                                                                                           | **Batasan**                                                                                                                               |
|----------------------|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Autentikasi dan akun | Registrasi/login JobX; role candidate, employer, admin; pengendalian akses berdasarkan role.                     | Login utama JobX tidak digantikan oleh GitHub OAuth.                                                                                      |
| Profil kandidat      | Headline, biografi, lokasi, pengalaman, preferensi kerja dan rentang gaji sesuai field database.                 | Tidak membangun profil sosial lengkap atau feed aktivitas.                                                                                |
| Company profile      | Employer membuat dan memperbarui satu profil perusahaan yang terhubung ke satu akun employer.                    | Satu akun employer hanya memiliki satu company_profile pada skema saat ini.                                                               |
| Smart Artifacts      | Tambah artifact; GitHub OAuth untuk memilih repository publik milik akun; simpan URL; input role dan kontribusi. | Repository privat tidak didukung. Analisis format non-GitHub dapat dibatasi pada format yang berhasil diimplementasikan selama hackathon. |
| Auto Skill Tagging   | Analisis artifact, normalisasi skill, evidence excerpt/lokasi, confidence, dan review kandidat.                  | Skill yang tidak ditemukan dinyatakan belum memiliki evidence di artifact, bukan otomatis tidak dimiliki kandidat.                        |
| Smart Job Descriptor | Input business problem; generasi draft JD; ekstraksi must-have/preferred skills; employer review dan approval.   | AI tidak boleh mengarang syarat yang tidak didukung input; employer tetap bertanggung jawab menyetujui JD.                                |
| Auto Matching        | Skor kecocokan, breakdown, alasan rekomendasi, daftar kandidat dan lowongan.                                     | Skor bukan probabilitas diterima atau prediksi performa kerja.                                                                            |
| Mutual swipe         | Keputusan accept/reject dari kandidat dan employer; status mutual acceptance.                                    | Chat, video interview, penjadwalan interview, dan penawaran kerja tidak termasuk MVP.                                                     |

## 5.2 Pengembangan Setelah MVP

- Analisis artifact tambahan seperti spreadsheet, gambar, video, dan tautan desain secara lebih mendalam.

- Dukungan repository privat melalui GitHub App dengan permission granular dan persetujuan repository tertentu.

- Verifikasi kontribusi oleh rekan project atau organisasi melalui mekanisme undangan dan konfirmasi.

- Chat antara kandidat dan employer setelah mutual acceptance.

- Penjadwalan interview, notifikasi, dan manajemen tahapan rekrutmen.

- Analisis ulang repository otomatis ketika ada perubahan pada commit atau branch.

- Pengelolaan beberapa perusahaan oleh satu akun recruiter apabila model bisnis memerlukannya.

## 5.3 Di Luar Ruang Lingkup

- JobX tidak menjamin kandidat akan diterima bekerja atau menjamin kualitas performa kerja hanya dari artifact.

- JobX tidak mengambil keputusan perekrutan final secara otomatis.

- JobX tidak mengubah, menghapus, atau menulis kode ke repository GitHub pengguna.

- JobX tidak mengakses repository privat pada MVP.

- JobX bukan sistem payroll, HRIS, atau manajemen karyawan setelah perekrutan.

- JobX tidak menjadikan swipe sebagai pengganti interview, asesmen teknis, pemeriksaan referensi, atau prosedur seleksi perusahaan.

# 6. Perjalanan Pengguna dan Alur Utama

## 6.1 Alur Kandidat

| **Tahap** | **Aktivitas**               | **Uraian**                                                                                                 |
|-----------|-----------------------------|------------------------------------------------------------------------------------------------------------|
| 01        | Registrasi dan profil       | Kandidat membuat akun JobX dengan account_type candidate dan melengkapi candidate_profile.                 |
| 02        | Hubungkan GitHub            | Kandidat memilih Connect GitHub dan memberikan otorisasi untuk identitas publik akun.                      |
| 03        | Pilih repository publik     | JobX menampilkan repository publik milik akun; kandidat memilih repository yang relevan.                   |
| 04        | Lengkapi informasi artifact | Kandidat memeriksa judul/deskripsi, menentukan peran, dan menjelaskan kontribusinya.                       |
| 05        | Impor artifact              | JobX membuat record artifact dengan source_url repository serta metadata relevan.                          |
| 06        | Analisis AI                 | Backend mengambil konten repository yang memenuhi kebijakan pemrosesan dan membuat artifact_analysis.      |
| 07        | Tinjau skill evidence       | Kandidat memeriksa skill, bukti, dan status; kandidat dapat mengonfirmasi atau menolak saran.              |
| 08        | Temukan pekerjaan           | Kandidat melihat lowongan yang direkomendasikan beserta alasan dan bukti kecocokan.                        |
| 09        | Berikan keputusan           | Kandidat menerima atau menolak rekomendasi; jika employer juga menerima, status menjadi mutually_accepted. |

## 6.2 Alur Employer

| **Tahap** | **Aktivitas**                    | **Uraian**                                                                                                               |
|-----------|----------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| 01        | Registrasi dan profil perusahaan | Employer membuat akun dan mengisi company_profile.                                                                       |
| 02        | Input kebutuhan bisnis           | Employer menjelaskan permasalahan, konteks posisi, lokasi, tipe pekerjaan, mode kerja, dan informasi lain yang tersedia. |
| 03        | Generasi Job Description         | AI menyusun draft JD dan mengekstrak skill wajib serta skill tambahan.                                                   |
| 04        | Review dan persetujuan           | Employer memperbaiki draft, menetapkan requirement, lalu menyetujui dan memublikasikan lowongan.                         |
| 05        | Tinjau rekomendasi kandidat      | Employer melihat kandidat yang cocok, score breakdown, penjelasan, dan artifact yang diizinkan untuk dilihat.            |
| 06        | Berikan keputusan                | Employer menerima atau menolak kandidat. Mutual acceptance terjadi jika kandidat juga menerima.                          |

## 6.3 Alur Integrasi GitHub OAuth untuk Repository Publik

> **KEPUTUSAN DESAIN MVP**  
> Integrasi menggunakan GitHub OAuth App untuk menghubungkan identitas akun dan mengambil daftar repository publik. JobX tidak membuat tabel github_connection. URL repository disimpan pada artifact.source_url dan metadata repository disimpan pada artifact.metadata.

| **Tahap** | **Aktivitas**            | **Uraian**                                                                                                                                                                                                        |
|-----------|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 01        | Mulai koneksi            | Pengguna JobX yang sudah login memilih tombol Connect GitHub pada area Smart Artifacts.                                                                                                                           |
| 02        | Arahkan ke GitHub        | Backend membuat authorization request dan parameter state acak untuk proteksi callback.                                                                                                                           |
| 03        | Otorisasi identitas      | Pengguna menyetujui proses OAuth. JobX hanya meminta akses minimum yang diperlukan untuk identitas publik; tidak meminta scope repo atau public_repo untuk MVP.                                                   |
| 04        | Callback dan validasi    | GitHub mengembalikan authorization code. Backend memvalidasi state, menukar code secara server-to-server, lalu menggunakan endpoint GET /user untuk membaca GitHub user id dan username akun yang terautentikasi. |
| 05        | Daftar repository publik | Backend meminta daftar repository publik milik username melalui GitHub REST API. Parameter type=owner, sort=updated, per_page maksimal 100, dan page digunakan untuk pagination.                                  |
| 06        | Pilih repository         | Frontend menampilkan nama repository, deskripsi, bahasa utama, visibility, waktu pembaruan, dan URL. Pengguna memilih satu repository.                                                                            |
| 07        | Input kontribusi         | Pengguna menjelaskan role dan kontribusi dalam repository. Sistem tidak menganggap pemilik akun sebagai bukti bahwa pengguna menulis seluruh kode.                                                                |
| 08        | Simpan artifact          | Backend memvalidasi URL dan kepemilikan repository, memeriksa duplikasi, lalu membuat artifact_type=github_repository dan menyimpan source_url serta metadata.                                                    |
| 09        | Mulai analisis           | JobX menjadwalkan analisis repository. Hasilnya dicatat melalui artifact_analysis dan artifact_skill_evidence.                                                                                                    |

Catatan teknis: Setelah callback OAuth, backend menggunakan GET /user untuk mengidentifikasi akun GitHub yang terautentikasi. Token OAuth tanpa scope tetap menerima respons profil publik; scope read:user hanya diperlukan untuk informasi profil privat tambahan \[8\]. Backend kemudian menggunakan endpoint “List repositories for a user” untuk menampilkan repository publik milik username tersebut. Endpoint dapat digunakan tanpa autentikasi apabila hanya resource publik yang diminta, serta mendukung per_page hingga 100 dan page untuk pagination \[5\]. Scope repo tidak diminta karena memberikan hak yang jauh lebih luas, termasuk akses tulis pada repository publik dan privat \[6\].

## 6.4 Alur Auto Skill Tagging

| **Tahap** | **Aktivitas**      | **Uraian**                                                                                                                  |
|-----------|--------------------|-----------------------------------------------------------------------------------------------------------------------------|
| 01        | Ingestion          | Backend mengambil metadata dan konten repository atau dokumen yang didukung.                                                |
| 02        | Penyaringan        | Sistem mengecualikan dependency, hasil build, file binary, file terlalu besar, serta pola file yang berisiko memuat secret. |
| 03        | Pemahaman artifact | AI membaca struktur project, README, file konfigurasi, source code terpilih, dan konteks role/kontribusi kandidat.          |
| 04        | Ekstraksi skill    | AI mengidentifikasi skill serta menghubungkannya ke master skill atau alias yang tersedia.                                  |
| 05        | Pembuatan evidence | Untuk setiap skill, AI menyertakan jenis evidence, excerpt, lokasi file, dan confidence.                                    |
| 06        | Validasi kandidat  | Kandidat meninjau dan mengonfirmasi/menolak saran; status review disimpan.                                                  |
| 07        | Pembaruan profil   | Sistem menyajikan agregasi skill berdasarkan evidence yang relevan dan status review.                                       |

## 6.5 Alur Smart Job Descriptor

| **Tahap** | **Aktivitas**      | **Uraian**                                                                          |
|-----------|--------------------|-------------------------------------------------------------------------------------|
| 01        | Input employer     | Employer memasukkan business_problem dan parameter pekerjaan yang diketahui.        |
| 02        | Analisis kebutuhan | AI mengidentifikasi tujuan posisi, tanggung jawab, kualifikasi, dan konteks kerja.  |
| 03        | Ekstraksi skill    | AI mengusulkan must_have dan preferred skills yang dapat dipetakan ke master skill. |
| 04        | Pembuatan draft    | Sistem membentuk job_summary dan job_description.                                   |
| 05        | Review employer    | Employer mengedit, menambah, atau menghapus informasi dan skill yang tidak sesuai.  |
| 06        | Publikasi          | Setelah disetujui, lowongan dipublikasikan dan dapat diproses oleh matching engine. |

## 6.6 Alur Auto Matching dan Mutual Swipe

| **Tahap** | **Aktivitas**          | **Uraian**                                                                                                     |
|-----------|------------------------|----------------------------------------------------------------------------------------------------------------|
| 01        | Persiapan data         | Sistem mengambil lowongan aktif serta evidence kandidat yang dapat digunakan sesuai aturan visibilitas.        |
| 02        | Perhitungan            | Matching engine menghitung komponen skill, kekuatan evidence, dan preferensi yang relevan.                     |
| 03        | Penjelasan             | Sistem menyusun alasan rekomendasi dan menyimpan score_breakdown.                                              |
| 04        | Distribusi rekomendasi | Kandidat melihat lowongan; employer melihat kandidat yang relevan untuk lowongannya.                           |
| 05        | Keputusan pertama      | Salah satu pihak menerima atau menolak; sistem memperbarui keputusan pihak tersebut.                           |
| 06        | Keputusan kedua        | Jika kedua pihak menerima, status menjadi mutually_accepted. Jika salah satu menolak, status menjadi rejected. |

# 7. Kebutuhan Fungsional

Kebutuhan fungsional diberi kode unik untuk memudahkan penelusuran antara requirement, implementasi backend/frontend, tabel database, dan pengujian. Prioritas P0 adalah wajib untuk demonstrasi alur inti MVP; P1 adalah kebutuhan pendukung yang dapat diselesaikan setelah alur inti berjalan.

| **ID**     | **Kebutuhan**                                                                                 | **Prioritas** | **Kriteria penerimaan ringkas**                                                                                              |
|------------|-----------------------------------------------------------------------------------------------|---------------|------------------------------------------------------------------------------------------------------------------------------|
| FR-AUTH-01 | Pengguna dapat membuat akun JobX dengan nama, email, password, dan tipe akun yang didukung.   | P0            | Akun baru tersimpan dengan email unik dan status active.                                                                     |
| FR-AUTH-02 | Pengguna dapat login dan logout dari JobX.                                                    | P0            | Akses sesi/token hanya diberikan setelah kredensial valid; logout membatalkan sesi sesuai implementasi.                      |
| FR-AUTH-03 | Sistem membatasi akses endpoint dan data berdasarkan account_type serta kepemilikan record.   | P0            | Candidate tidak dapat mengubah lowongan employer; employer tidak dapat mengubah artifact kandidat.                           |
| FR-CAN-01  | Candidate dapat membuat dan memperbarui candidate_profile.                                    | P0            | Perubahan profil tersimpan dan hanya dapat dilakukan oleh pemilik atau admin berwenang.                                      |
| FR-EMP-01  | Employer dapat membuat dan memperbarui company_profile.                                       | P0            | Satu akun employer hanya memiliki satu company_profile pada skema saat ini.                                                  |
| FR-ART-01  | Candidate dapat membuat artifact dari sumber yang didukung dan mengisi judul serta deskripsi. | P0            | Record artifact terhubung ke owner_user_id dan memiliki source_url atau storage_key yang valid.                              |
| FR-ART-02  | Candidate dapat menghubungkan identitas GitHub melalui OAuth.                                 | P0            | Callback divalidasi menggunakan state; identitas GitHub yang diterima sesuai dengan akun yang mengotorisasi.                 |
| FR-ART-03  | Sistem menampilkan repository publik yang dimiliki akun GitHub terhubung.                     | P0            | Daftar hanya berisi repository publik; pagination tersedia jika lebih dari satu halaman.                                     |
| FR-ART-04  | Candidate dapat memilih repository publik dan mengimpornya sebagai artifact.                  | P0            | Artifact dibuat dengan type github_repository, source_url, metadata repository, serta owner_user_id akun JobX.               |
| FR-ART-05  | Candidate dapat menjelaskan role dan kontribusi pada artifact.                                | P0            | Role dan contribution_description tercatat pada artifact_contribution.                                                       |
| FR-ART-06  | Candidate dapat melihat, memperbarui deskripsi/visibility, dan menghapus artifact miliknya.   | P0            | Operasi hanya berlaku pada artifact pemilik; penghapusan juga membersihkan file terkait sesuai kebijakan storage.            |
| FR-ART-07  | Sistem mendeteksi kemungkinan impor repository yang sama oleh pemilik JobX yang sama.         | P1            | Sistem memberi peringatan atau menolak duplikasi berdasarkan URL/repository id yang dinormalisasi.                           |
| FR-AI-01   | Sistem menjalankan analisis artifact secara asinkron.                                         | P0            | Status berpindah queued → processing → completed/failed/needs_review.                                                        |
| FR-AI-02   | AI mengidentifikasi skill yang berkaitan dengan artifact dan kontribusi kandidat.             | P0            | Skill hasil analisis mengacu pada master skill atau masuk tahap normalisasi.                                                 |
| FR-AI-03   | Setiap skill hasil AI memiliki jenis evidence, excerpt/lokasi, dan confidence score.          | P0            | Evidence dapat ditelusuri ke file atau bagian artifact; confidence berada dalam rentang 0–1.                                 |
| FR-AI-04   | Candidate dapat meninjau, mengonfirmasi, atau menolak skill yang disarankan.                  | P0            | review_status diperbarui menjadi candidate_confirmed atau rejected.                                                          |
| FR-AI-05   | Sistem menyimpan model, versi prompt, ringkasan, hasil mentah, dan error analisis.            | P0            | Riwayat analisis tercatat pada artifact_analysis untuk keperluan audit dan evaluasi.                                         |
| FR-JOB-01  | Employer dapat membuat lowongan dengan business_problem dan parameter pekerjaan.              | P0            | Lowongan terhubung langsung ke user_id employer dan berstatus draft secara default.                                          |
| FR-JOB-02  | AI dapat membuat draft job_summary dan job_description dari input employer.                   | P0            | Draft tersimpan dan dapat diedit employer sebelum disetujui.                                                                 |
| FR-JOB-03  | AI mengidentifikasi skill must_have dan preferred untuk lowongan.                             | P0            | Skill requirement menggunakan skill_id, requirement_type, minimum_level bila ditentukan, dan weight.                         |
| FR-JOB-04  | Employer dapat meninjau, mengubah, menyetujui, dan memublikasikan lowongan.                   | P0            | Hanya employer pemilik lowongan yang dapat melakukan perubahan; approval dan publication status konsisten.                   |
| FR-JOB-05  | Employer dapat menjeda atau menutup lowongan.                                                 | P1            | Lowongan yang paused/closed tidak menghasilkan rekomendasi baru.                                                             |
| FR-MAT-01  | Sistem menghitung kecocokan antara candidate dan job_post yang aktif.                         | P0            | Skor 0–100 disimpan bersama waktu perhitungan.                                                                               |
| FR-MAT-02  | Sistem menampilkan score breakdown dan explanation.                                           | P0            | Penjelasan memuat skill yang cocok, skill yang belum memiliki evidence, dan faktor preferensi yang digunakan.                |
| FR-MAT-03  | Candidate dapat menerima atau menolak rekomendasi pekerjaan.                                  | P0            | candidate_decision dan candidate_decided_at diperbarui.                                                                      |
| FR-MAT-04  | Employer dapat menerima atau menolak kandidat pada lowongannya.                               | P0            | employer_decision dan employer_decided_at diperbarui oleh employer pemilik lowongan.                                         |
| FR-MAT-05  | Sistem mengelola status mutual interest berdasarkan dua keputusan.                            | P0            | Kedua accepted → mutually_accepted; salah satu rejected → rejected; satu accepted dan lainnya pending → one_side_interested. |
| FR-MAT-06  | Sistem tidak menampilkan artifact yang tidak memiliki izin visibilitas untuk employer.        | P0            | Pengujian otorisasi membuktikan data private tidak dapat diakses employer.                                                   |
| FR-ADM-01  | Admin dapat mengelola master skill dan alias untuk normalisasi.                               | P1            | Skill canonical dan alias dapat dibuat/diperbarui sesuai hak akses admin.                                                    |

# 8. Persyaratan Sistem AI

## 8.1 Prinsip Umum AI

Komponen AI digunakan untuk mengekstrak dan menyusun informasi, bukan sebagai otoritas tunggal yang menetapkan kompetensi atau memutuskan kelayakan kerja. Seluruh output AI yang berdampak pada profil kandidat atau lowongan harus dapat ditinjau dan dikoreksi oleh pengguna yang relevan.

## 8.2 Artifact Analysis

| **Aspek**   | **Persyaratan**                                                                                                                                                                   |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Input       | Metadata artifact, isi repository/dokumen yang lolos penyaringan, deskripsi project, role kandidat, dan contribution_description.                                                 |
| Analisis    | Mengenali domain project, fungsi sistem, arsitektur/komponen, teknologi, dan aktivitas yang terlihat dari artifact.                                                               |
| Output      | Ringkasan artifact; daftar skill canonical; kategori; evidence type; confidence; excerpt; evidence_location; dan catatan keterbatasan.                                            |
| Penyimpanan | artifact_analysis menyimpan status, provider/model, prompt_version, extracted_summary, raw_result, dan error_message. artifact_skill_evidence menyimpan tiap skill beserta bukti. |
| Validasi    | Kandidat dapat menerima/menolak saran. Reviewer manusia dapat melakukan verifikasi bila fitur review tersedia.                                                                    |

## 8.3 Standar Skill Evidence

| **Atribut**              | **Makna dan aturan**                                                                                                                                        |
|--------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| canonical skill          | Nama skill standar yang berasal dari tabel skill.                                                                                                           |
| evidence_kind = direct   | Artifact secara langsung memperlihatkan penggunaan atau konfigurasi teknologi/kompetensi, misalnya dependency, endpoint, query, atau komponen implementasi. |
| evidence_kind = inferred | Skill disimpulkan dari pola atau struktur artifact; harus dijelaskan sebagai inferensi.                                                                     |
| confidence_score         | Keyakinan model terhadap identifikasi/pemetaan skill, bukan probabilitas kandidat benar-benar menguasai skill.                                              |
| evidence_excerpt         | Potongan konten ringkas yang mendukung identifikasi.                                                                                                        |
| evidence_location        | Lokasi bukti, misalnya path file dan rentang baris/section bila tersedia.                                                                                   |
| review_status            | ai_suggested, candidate_confirmed, reviewer_verified, atau rejected.                                                                                        |

> **ATURAN PENTING**  
> Tidak ditemukannya bukti pada artifact tidak boleh ditampilkan sebagai bukti bahwa kandidat tidak menguasai skill. Gunakan istilah “belum ditemukan evidence pada artifact yang dianalisis”. AI confidence juga tidak boleh dipresentasikan sebagai ukuran kemampuan nyata kandidat.

## 8.4 Penyaringan dan Keamanan Repository

- Sistem memprioritaskan README, konfigurasi dependency, struktur direktori, file source code yang relevan, dokumentasi API, dan skema data.

- Sistem mengecualikan folder dependency dan hasil build seperti node_modules, .venv, vendor, dist, build, serta file binary atau file yang tidak relevan.

- Sistem harus menghindari pemrosesan file rahasia seperti .env, private key, credential, token, serta file konfigurasi sensitif. Pengecualian berbasis nama/path perlu dilengkapi deteksi pola rahasia.

- Konten repository diperlakukan sebagai data tidak tepercaya. Instruksi yang tertanam dalam README, komentar source code, atau dokumen tidak boleh mengubah instruksi sistem AI (mitigasi prompt injection).

- Batas jumlah file dan ukuran total yang dianalisis ditetapkan sebagai konfigurasi aplikasi. Repository yang melampaui batas diberi status needs_review atau pesan keterbatasan, bukan gagal tanpa penjelasan.

- Analisis mencatat commit SHA atau identitas revisi yang dianalisis pada metadata agar hasil dapat ditelusuri ke versi repository.

## 8.5 Smart Job Descriptor

| **Input employer**                           | **Output AI yang diharapkan**                                                                |
|----------------------------------------------|----------------------------------------------------------------------------------------------|
| Business problem                             | Ringkasan tujuan dan konteks pekerjaan.                                                      |
| Informasi posisi (jika diketahui)            | Job title, employment type, work mode, lokasi, dan rentang kompensasi sesuai input employer. |
| Konteks perusahaan/industri (jika diberikan) | Tanggung jawab, hasil kerja yang diharapkan, dan konteks kolaborasi.                         |
| Kebutuhan kompetensi (jika disebutkan)       | Must-have skills, preferred skills, minimum level jika didukung informasi.                   |

AI tidak boleh mengarang tingkat senioritas, pendidikan wajib, pengalaman minimum, gaji, benefit, lokasi, atau persyaratan lain yang tidak diberikan atau tidak dapat disimpulkan secara wajar. Informasi yang belum tersedia harus dibiarkan kosong atau ditandai untuk dilengkapi employer.

## 8.6 Matching Explanation

- Menjelaskan skill wajib yang memiliki evidence dan evidence yang masih berupa saran AI.

- Menunjukkan skill preferred yang terdeteksi, tidak terdeteksi, atau belum dianalisis.

- Menjelaskan kesesuaian preferensi kerja yang datanya tersedia, seperti tipe pekerjaan, mode kerja, lokasi, dan gaji yang diharapkan.

- Menampilkan keterbatasan data jika jumlah artifact atau evidence kandidat belum mencukupi.

## 8.7 Pengawasan Manusia

Kandidat mengendalikan informasi kontribusi dan dapat meninjau saran skill. Employer meninjau draft JD sebelum publikasi dan menentukan sendiri apakah kandidat akan diteruskan ke tahap berikutnya. AI tidak boleh menolak kandidat secara final, mengirim penawaran kerja, atau mengubah keputusan employer secara otomatis.

# 9. Aturan Bisnis dan Logika Pencocokan

## 9.1 Aturan Akun dan Kepemilikan

- Email pada user harus unik. account_type yang didukung adalah candidate, employer, dan admin; account_status adalah active atau inactive.

- candidate_profile hanya dimiliki akun candidate. company_profile hanya dimiliki akun employer. Validasi tipe akun dilaksanakan oleh backend karena foreign key tidak memeriksa nilai account_type.

- Satu akun employer hanya memiliki satu company_profile berdasarkan unique user_id pada skema saat ini.

- job_post.user_id harus merujuk ke akun employer dan menjadi pemilik lowongan. Profil perusahaan diambil melalui company_profile.user_id yang sama.

- job_match.candidate_user_id harus merujuk ke akun candidate; job_id harus merupakan lowongan yang aktif dan memenuhi syarat rekomendasi.

- Pengguna hanya dapat memperbarui atau menghapus data yang dimilikinya, kecuali tindakan administratif yang secara eksplisit diizinkan.

## 9.2 Aturan Artifact dan GitHub

- Satu repository yang dipilih menjadi satu record artifact dengan artifact_type github_repository.

- Untuk GitHub import pada MVP, hanya repository public yang dimiliki akun GitHub yang sedang diotorisasi yang ditampilkan (type=owner). Repository organisasi atau repository kolaborasi yang tidak dimiliki akun tidak menjadi cakupan utama MVP.

- URL repository disimpan pada artifact.source_url. Metadata provider, GitHub user id/username, repository id, full_name, default_branch, bahasa, visibility, dan commit SHA dapat disimpan pada artifact.metadata.

- GitHub OAuth hanya untuk menghubungkan identitas dan memilih repository publik. Token tidak disimpan permanen; backend tidak meminta scope repo atau public_repo dan tidak melakukan operasi tulis.

- JobX tidak mengubah repository asli. Penghapusan artifact hanya menghapus data/rujukan dalam JobX dan file salinan sementara sesuai kebijakan; tidak menghapus repository pada GitHub.

- Pengguna wajib menyatakan peran dan kontribusinya. Kepemilikan akun GitHub atau akses ke repository bukan bukti bahwa pengguna menulis seluruh kode.

- Sistem memeriksa kemungkinan duplikasi repository untuk owner_user_id yang sama berdasarkan canonical repository URL atau repository id dalam metadata.

## 9.3 Aturan Job Posting

- Business problem wajib diisi sebelum AI membuat draft JD.

- Employer melengkapi employment_type dan work_mode karena field tersebut wajib pada skema job_post.

- AI menghasilkan draft. Employer dapat mengedit sebelum approval_status menjadi approved dan publication_status menjadi published.

- Hanya lowongan yang approved, published, belum ditutup, dan memenuhi filter lokasi/jenis kerja yang dapat digunakan untuk rekomendasi.

- Skill pada lowongan harus dihubungkan ke tabel skill melalui job_skill_requirement; satu skill tidak boleh didaftarkan dua kali pada lowongan yang sama.

- Rentang gaji harus valid: salary_min tidak boleh lebih besar daripada salary_max jika keduanya diisi.

## 9.4 Rancangan Awal Skor Matching

Matching engine menggunakan gabungan kecocokan keterampilan wajib, keterampilan tambahan, kekuatan evidence, dan preferensi kerja. Formula berikut merupakan hipotesis awal untuk MVP dan harus dievaluasi melalui pengujian; bobot bukan hasil penelitian validasi JobX.

| Match Score = 0,50 × S_required + 0,20 × S_preferred + 0,20 × E_quality + 0,10 × P_compatibility |
|--------------------------------------------------------------------------------------------------|

| **Komponen**    | **Definisi**                                                                                         |
|-----------------|------------------------------------------------------------------------------------------------------|
| S_required      | Tingkat ketercakupan skill must_have berdasarkan evidence yang tersedia.                             |
| S_preferred     | Tingkat ketercakupan skill preferred.                                                                |
| E_quality       | Kualitas evidence: direct/inferred, lokasi bukti, status review, dan konsistensi analisis.           |
| P_compatibility | Kesesuaian preferensi tipe pekerjaan, mode kerja, lokasi, dan rentang gaji apabila datanya tersedia. |

Perhitungan setiap komponen dinormalisasi pada rentang 0–100. Bila suatu informasi preferensi tidak tersedia, sistem sebaiknya tidak menganggapnya sebagai ketidakcocokan; komponen tersebut dapat dikecualikan dan bobot komponen lain dinormalisasi kembali. Ambang “fit” atau urutan rekomendasi harus dapat dikonfigurasi. Skor menunjukkan relevansi berdasarkan informasi yang tersedia di JobX, bukan probabilitas keberhasilan kerja atau peluang diterima.

## 9.5 Aturan Mutual Swipe

| **Keputusan kandidat** | **Keputusan employer**    | **Status match**    |
|------------------------|---------------------------|---------------------|
| pending                | pending                   | recommended         |
| accepted               | pending                   | one_side_interested |
| pending                | accepted                  | one_side_interested |
| accepted               | accepted                  | mutually_accepted   |
| rejected               | pending/accepted/rejected | rejected            |
| pending/accepted       | rejected                  | rejected            |

Satu pasangan job_id dan candidate_user_id hanya memiliki satu record job_match sesuai unique constraint. Keputusan hanya dapat diubah oleh pihak yang bersangkutan dan harus terkait dengan job yang dimiliki employer. Status expired dapat digunakan apabila rekomendasi tidak lagi berlaku, misalnya lowongan ditutup atau masa rekomendasi berakhir.

## 9.6 Aturan Visibilitas Artifact

| **Visibility**     | **Perilaku yang diharapkan**                                                                           |
|--------------------|--------------------------------------------------------------------------------------------------------|
| private            | Hanya pemilik dan admin yang berwenang dapat melihat.                                                  |
| unlisted           | Tidak muncul pada penelusuran publik; akses diberikan melalui mekanisme tautan/izin yang dibatasi.     |
| matching_employers | Dapat diperlihatkan kepada employer yang berwenang melihat rekomendasi terkait, sesuai kebijakan JobX. |
| public             | Dapat dilihat oleh pengguna umum sesuai halaman dan kebijakan platform.                                |

# 10. Persyaratan Nonfungsional

| **ID** | **Kategori**                 | **Persyaratan**                                                                                                                                                                                                              |
|--------|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| NFR-01 | Keamanan autentikasi         | Password disimpan menggunakan hashing yang kuat; token dan secret diletakkan di server-side environment/secret manager; endpoint dilindungi autentikasi dan otorisasi.                                                       |
| NFR-02 | Keamanan OAuth GitHub        | Parameter state harus divalidasi; authorization code ditukar di backend; token tidak dikirim ke browser atau disimpan permanen untuk MVP; scope repository privat tidak diminta.                                             |
| NFR-03 | Privasi dan pelindungan data | Pengguna diberi informasi tentang data yang diproses, tujuan analisis AI, visibilitas artifact, dan mekanisme penghapusan. Implementasi perlu ditinjau terhadap UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi \[7\]. |
| NFR-04 | Kontrol akses                | Data kandidat, employer, company_profile, artifact, job_post, dan job_match harus dilindungi pemeriksaan pemilik dan role pada backend.                                                                                      |
| NFR-05 | Kinerja API                  | Target awal untuk operasi CRUD internal adalah p95 ≤ 2 detik pada beban demo yang disepakati, tidak termasuk waktu respons pihak ketiga GitHub dan model AI. Target ini harus diuji.                                         |
| NFR-06 | Pemrosesan asinkron          | Analisis artifact dan generasi AI tidak boleh mengunci request web dalam waktu lama; pengguna melihat status queued, processing, completed, failed, atau needs_review.                                                       |
| NFR-07 | Keandalan integrasi          | Sistem menangani timeout, rate limit, pagination, repository tidak tersedia, perubahan visibility, dan kegagalan GitHub API dengan pesan yang dapat ditindaklanjuti.                                                         |
| NFR-08 | Keterlacakan                 | Setiap analisis mencatat provider, model, prompt_version, waktu proses, ringkasan, dan status untuk membantu debugging dan evaluasi.                                                                                         |
| NFR-09 | Konsistensi data             | Relasi foreign key, unique constraint, check constraint, serta validasi role/ownership di service layer harus dijaga.                                                                                                        |
| NFR-10 | Kegunaan                     | Pengguna memahami perbedaan skill yang terdeteksi, inferred, dikonfirmasi kandidat, dan diverifikasi reviewer.                                                                                                               |
| NFR-11 | Ketersediaan                 | Kegagalan GitHub atau model AI tidak boleh menghapus artifact atau profil yang sudah tersimpan; analisis dapat dicoba kembali secara terkendali.                                                                             |
| NFR-12 | Fairness dan transparansi    | Rekomendasi tidak menggunakan atribut sensitif yang tidak relevan; sistem menyediakan penjelasan dan tetap memberi ruang keputusan manusia. Risiko bias perlu dievaluasi berkala \[4\].                                      |

# 11. Persyaratan Data dan Basis Data

## 11.1 Acuan Skema

PRD ini mengikuti file SQL JobX versi kompatibel terbaru yang telah direvisi: nama tabel singular, tabel company dan company_member dihapus, company_profile ditambahkan dan terhubung satu-ke-satu dengan user, serta job_post terhubung langsung ke user melalui user_id. Field website_url dan verification_status tidak digunakan pada company_profile. Collation database menggunakan utf8mb4_unicode_ci untuk menghindari error utf8mb4_0900_ai_ci pada lingkungan yang tidak mendukung collation tersebut.

## 11.2 Daftar Tabel

| **Kelompok**      | **Tabel**               | **Tanggung jawab**                                                                                   |
|-------------------|-------------------------|------------------------------------------------------------------------------------------------------|
| Akun dan profil   | user                    | Identitas akun, email, password_hash, account_type, account_status.                                  |
| Akun dan profil   | candidate_profile       | Informasi kandidat, lokasi, pengalaman, preferensi kerja, ekspektasi gaji, visibilitas profil.       |
| Akun dan profil   | company_profile         | Profil perusahaan yang dimiliki satu akun employer melalui user_id.                                  |
| Master kompetensi | skill                   | Master nama skill, kategori, deskripsi, hierarki skill.                                              |
| Master kompetensi | skill_alias             | Sinonim/nama alternatif yang dipetakan ke skill canonical.                                           |
| Artifact          | artifact                | Metadata karya kandidat, source_url/storage_key, visibility, status proses, metadata JSON.           |
| Artifact          | artifact_contribution   | Peran, deskripsi kontribusi, persentase klaim kontribusi, dan status klaim.                          |
| Analisis AI       | artifact_analysis       | Riwayat analisis, model, prompt version, ringkasan, raw output, error, dan review.                   |
| Analisis AI       | artifact_skill_evidence | Relasi artifact-analysis-skill serta confidence, jenis evidence, excerpt, lokasi, dan status review. |
| Pekerjaan         | job_post                | Business problem, Job Description, parameter kerja, status approval dan publikasi.                   |
| Pekerjaan         | job_skill_requirement   | Skill yang wajib atau diutamakan pada sebuah lowongan beserta bobot.                                 |
| Matching          | job_match               | Skor dan explanation, keputusan candidate/employer, serta status mutual matching.                    |

Total: 12 tabel. Integrasi GitHub MVP tidak menambahkan tabel github_connection. Identitas repository disimpan di artifact.source_url dan artifact.metadata.

## 11.3 Relasi Utama

| **Relasi**                                  | **Kardinalitas / aturan**                                                                                                          |
|---------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| user → candidate_profile                    | Satu akun candidate memiliki nol atau satu profil kandidat; candidate_profile.user_id merupakan primary key sekaligus foreign key. |
| user → company_profile                      | Satu akun employer memiliki nol atau satu company_profile; company_profile.user_id unik.                                           |
| user → artifact                             | Satu kandidat dapat memiliki banyak artifact melalui artifact.owner_user_id.                                                       |
| artifact → artifact_contribution            | Satu artifact dapat memiliki satu atau lebih record kontribusi.                                                                    |
| artifact → artifact_analysis                | Satu artifact dapat dianalisis berkali-kali; riwayat analisis disimpan.                                                            |
| artifact_analysis → artifact_skill_evidence | Satu analisis dapat menghasilkan banyak evidence skill.                                                                            |
| skill → skill_alias                         | Satu skill dapat memiliki beberapa alias.                                                                                          |
| job_post → job_skill_requirement            | Satu lowongan dapat memiliki banyak persyaratan skill.                                                                             |
| job_post ↔ candidate melalui job_match      | Relasi many-to-many yang menyimpan skor dan keputusan kedua pihak; satu pasangan job-candidate dibatasi satu record.               |

## 11.4 Pemetaan Data GitHub ke Tabel Artifact

| **Kolom artifact** | **Nilai untuk GitHub import**                                                                                                                                         |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| owner_user_id      | ID akun JobX kandidat yang sedang login.                                                                                                                              |
| title              | Nama repository yang dipilih, misalnya hospital-management-system.                                                                                                    |
| artifact_type      | github_repository.                                                                                                                                                    |
| description        | Deskripsi repository dari GitHub dan/atau deskripsi tambahan dari kandidat.                                                                                           |
| source_url         | URL canonical repository, misalnya https://github.com/username/repository.                                                                                            |
| storage_key        | NULL untuk referensi URL GitHub jika tidak membuat salinan file.                                                                                                      |
| visibility         | Nilai yang ditentukan pengguna sesuai pilihan berbagi pada JobX; repository GitHub tetap public di GitHub.                                                            |
| processing_status  | not_started/queued/processing/completed/failed/needs_review.                                                                                                          |
| metadata           | JSON berisi provider, github_user_id, github_username, repository_id, full_name, default_branch, language, pushed_at, analyzed_commit_sha, dan metadata yang relevan. |

```json
{
  "provider": "github",
  "github_user_id": 12345,
  "github_username": "candidate-handle",
  "repository_id": 987654,
  "repository_full_name": "candidate-handle/hospital-management-system",
  "default_branch": "main",
  "language": "Python",
  "analyzed_commit_sha": "<commit-sha>",
  "visibility": "public"
}
```

## 11.5 Catatan Integritas Data

- Backend harus memastikan company_profile.user_id dan job_post.user_id dimiliki akun dengan account_type employer; candidate_profile.user_id dan job_match.candidate_user_id harus dimiliki akun candidate.

- Backend harus memastikan artifact_skill_evidence.artifact_id sama dengan artifact_analysis.artifact_id pada analysis_id yang dirujuk. Skema saat ini memiliki dua foreign key terpisah dan tidak dengan sendirinya menjamin kesamaan pasangan tersebut.

- Backend harus memvalidasi bahwa job_post yang menjadi induk job_match masih relevan dan dimiliki employer yang memberikan keputusan.

- Penghapusan artifact perlu menghapus hasil analisis dan evidence terkait sesuai cascade pada database serta menghapus file sementara dari object storage bila ada.

- Raw output AI pada JSON harus dibatasi agar tidak menyimpan secret, token, atau data pribadi yang tidak diperlukan.

# 12. Arsitektur Teknis dan Integrasi

## 12.1 Tumpukan Teknologi

| **Lapisan**          | **Teknologi acuan**                          | **Tanggung jawab**                                                                                       |
|----------------------|----------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Frontend             | React JS, Tailwind CSS, shadcn/ui            | Antarmuka kandidat/employer, pemilihan repository, formulir input, review AI, kartu matching, dan swipe. |
| Backend API          | Python, FastAPI                              | Autentikasi, otorisasi, validasi data, endpoint, orkestrasi proses, dan integrasi eksternal.             |
| AI orchestration     | LangChain, LangGraph                         | Workflow artifact analysis, skill extraction, job descriptor, dan matching explanation.                  |
| Database             | MySQL                                        | Penyimpanan akun, profil, artifact, skill/evidence, lowongan, dan matching.                              |
| File storage         | Object storage atau storage server yang aman | Penyimpanan file artifact yang diunggah, bukan binary dalam kolom MySQL.                                 |
| External integration | GitHub OAuth App dan GitHub REST API         | Otorisasi identitas GitHub dan pengambilan daftar repository publik.                                     |

## 12.2 Pembagian Tanggung Jawab Sistem

| **Komponen**       | **Tanggung jawab**                                                                                                                                                |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Frontend           | Mengumpulkan input, menampilkan repository, mengirim pilihan, menampilkan status analisis dan hasil evidence, serta menyediakan tampilan matching.                |
| FastAPI            | Memastikan user yang aktif, memvalidasi role dan kepemilikan, menangani callback OAuth, memanggil GitHub API, menulis database, serta menjalankan layanan bisnis. |
| LangGraph workflow | Mengatur urutan ekstraksi, penyaringan, analisis, normalisasi skill, evidence generation, dan penyusunan penjelasan.                                              |
| MySQL              | Menjadi sumber data utama untuk entitas dan status proses. Hasil AI disimpan agar dapat ditinjau kembali.                                                         |
| GitHub API         | Menyediakan identitas publik dan daftar repository publik yang dimiliki akun.                                                                                     |

## 12.3 Usulan Endpoint Backend

| **Metode dan endpoint (usulan)**                                 | **Fungsi**                                                      |
|------------------------------------------------------------------|-----------------------------------------------------------------|
| POST /api/v1/auth/register                                       | Registrasi akun JobX.                                           |
| POST /api/v1/auth/login                                          | Login ke JobX.                                                  |
| GET /api/v1/integrations/github/authorize                        | Memulai proses GitHub OAuth.                                    |
| GET /api/v1/integrations/github/callback                         | Menangani callback OAuth dan memvalidasi state.                 |
| GET /api/v1/integrations/github/repositories?page=1&per_page=100 | Mengambil daftar repository publik milik akun yang terhubung.   |
| POST /api/v1/artifacts/github/import                             | Membuat artifact dari repository yang dipilih.                  |
| GET /api/v1/artifacts                                            | Menampilkan artifact milik kandidat.                            |
| POST /api/v1/artifacts/{artifact_id}/analyze                     | Memulai atau mengulang analisis artifact.                       |
| GET /api/v1/artifacts/{artifact_id}/analysis                     | Mengambil status dan hasil analisis.                            |
| PATCH /api/v1/artifact-skill-evidence/{evidence_id}              | Memperbarui keputusan kandidat terhadap skill evidence.         |
| POST /api/v1/jobs/generate-description                           | Menghasilkan draft Job Description dari business problem.       |
| POST /api/v1/jobs                                                | Membuat lowongan.                                               |
| PATCH /api/v1/jobs/{job_id}/publish                              | Menyetujui dan memublikasikan lowongan.                         |
| GET /api/v1/matches/candidate                                    | Mengambil rekomendasi pekerjaan untuk kandidat.                 |
| GET /api/v1/jobs/{job_id}/matches                                | Mengambil rekomendasi kandidat untuk employer pemilik lowongan. |
| POST /api/v1/matches/{match_id}/candidate-decision               | Menyimpan keputusan candidate.                                  |
| POST /api/v1/matches/{match_id}/employer-decision                | Menyimpan keputusan employer.                                   |

Endpoint di atas merupakan rancangan kontrak API tingkat produk, bukan definisi final OpenAPI. Nama path, payload, status HTTP, autentikasi, dan skema response perlu difinalisasi saat implementasi backend.

## 12.4 Keamanan Integrasi GitHub

- GitHub OAuth App dikonfigurasi pada sisi GitHub dengan callback URL yang sesuai. Client secret disimpan hanya di konfigurasi server.

- Backend membuat state acak yang terikat pada sesi pengguna JobX dan memvalidasinya ketika callback diterima untuk mengurangi risiko CSRF.

- Authorization code ditukar di backend. Token tidak pernah ditanamkan dalam JavaScript frontend atau dicatat ke log.

- Untuk MVP, tidak meminta scope repo atau public_repo. GitHub mendokumentasikan bahwa scope kosong memberi akses baca pada informasi publik, sedangkan repo memberikan hak luas termasuk baca/tulis pada repository publik dan privat \[6\].

- Pengambilan daftar public repository memakai endpoint GET /users/{username}/repos dengan type=owner, sort=updated, per_page sampai 100, dan page. API dapat digunakan tanpa autentikasi bila hanya resource publik diminta \[5\].

- Backend hanya menerima repository yang public dan owner.login sesuai identitas akun GitHub yang sedang terhubung. URL juga divalidasi sebagai host github.com untuk mencegah SSRF atau URL arbitrer.

- Rate limit, pagination, repository yang dihapus/diubah menjadi privat, dan kegagalan API ditangani dengan pesan dan retry yang terkendali.

- Access token tidak disimpan permanen pada database dalam desain MVP. Jika suatu saat diperlukan sinkronisasi atau akses repository privat, desain otorisasi harus dievaluasi kembali; GitHub App lebih sesuai untuk permission granular.

## 12.5 Gambaran Aliran Data

| **Aliran**              | **Data masuk**                                        | **Proses / penyimpanan**                                           | **Keluaran**                                                  |
|-------------------------|-------------------------------------------------------|--------------------------------------------------------------------|---------------------------------------------------------------|
| Artifact to evidence    | Repository URL, metadata GitHub, role dan kontribusi. | Ingestion → filter → AI analysis → skill normalization → evidence. | Ringkasan artifact dan skill evidence.                        |
| Business problem to job | Business problem dan parameter posisi.                | AI job descriptor → employer review → job_skill_requirement.       | JD dan lowongan terstruktur.                                  |
| Job to candidate match  | Job skill requirement dan candidate evidence.         | Matching service menghitung skor dan menyimpan explanation.        | Rekomendasi kandidat/lowongan.                                |
| Mutual interest         | Keputusan candidate dan employer.                     | Pembaruan dua kolom keputusan pada job_match.                      | Status one_side_interested, mutually_accepted, atau rejected. |

# 13. Kriteria Penerimaan dan Strategi Pengujian

## 13.1 Skenario Uji Penerimaan MVP

| **ID** | **Skenario**               | **Kriteria penerimaan**                                                                                                                |
|--------|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| AT-01  | Registrasi kandidat        | Kandidat dapat mendaftar, login, dan membuat profil tanpa memperoleh akses ke fungsi employer.                                         |
| AT-02  | Registrasi employer        | Employer dapat membuat akun dan company_profile; akun candidate tidak dapat membuat company_profile.                                   |
| AT-03  | GitHub OAuth berhasil      | Pengguna dapat mengotorisasi GitHub dan callback state yang valid menghasilkan identitas GitHub yang sesuai.                           |
| AT-04  | GitHub OAuth gagal/ditolak | Sistem menampilkan pesan yang aman, tidak membuat artifact, dan tidak membocorkan token.                                               |
| AT-05  | Daftar repository publik   | Hanya repository publik yang dimiliki username terhubung ditampilkan; pagination berfungsi pada akun dengan lebih dari 100 repository. |
| AT-06  | Repository tidak valid     | Repository privat, URL host selain github.com, atau repository yang bukan milik akun tidak dapat diimpor melalui alur MVP.             |
| AT-07  | Impor artifact             | Satu repository terpilih membuat satu record artifact dengan source_url dan metadata repository; tidak ada tabel koneksi GitHub baru.  |
| AT-08  | Duplikasi artifact         | Impor repository yang sama oleh pemilik yang sama menghasilkan peringatan/penanganan duplikasi.                                        |
| AT-09  | Kontribusi kandidat        | Role dan deskripsi kontribusi wajib tersedia sebelum analisis akhir dimulai atau sebelum artifact dinyatakan siap dianalisis.          |
| AT-10  | AI analysis berhasil       | Analisis yang berhasil menampilkan summary, skill, evidence excerpt/lokasi, evidence type, confidence, dan status.                     |
| AT-11  | Analisis gagal             | Kesalahan GitHub/LLM menghasilkan status failed atau needs_review, pesan yang dapat dipahami, dan opsi retry.                          |
| AT-12  | Skill evidence review      | Kandidat dapat mengonfirmasi atau menolak skill; hasil tidak mengubah source repository.                                               |
| AT-13  | Generasi JD                | Employer memasukkan business problem, menerima draft, mengeditnya, dan mengubah status sesuai workflow persetujuan.                    |
| AT-14  | Matching explanation       | Kandidat/employer melihat skor beserta komponen dan alasan; skill yang tidak terbukti ditandai belum ada evidence.                     |
| AT-15  | Mutual acceptance          | Keputusan dua pihak menghasilkan status yang sesuai tabel aturan mutual swipe.                                                         |
| AT-16  | Isolasi data               | Pengguna tidak dapat membaca/mengubah artifact, profil, lowongan, atau keputusan milik pengguna lain tanpa hak akses.                  |
| AT-17  | Privasi artifact           | Artifact private tidak dapat diakses employer melalui daftar matching atau endpoint detail.                                            |

## 13.2 Jenis Pengujian

| **Jenis**        | **Fokus pengujian**                                                                                                           |
|------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Unit test        | Validasi service, normalisasi skill, aturan skor, pembaruan status swipe, dan pemeriksaan role.                               |
| Integration test | Integrasi MySQL, GitHub OAuth callback, GitHub public repositories API, object storage bila digunakan, dan pipeline AI.       |
| Functional test  | Registrasi, profil, impor artifact, analisis, pembuatan lowongan, matching, dan mutual decision.                              |
| Security test    | CSRF pada OAuth state, token leakage, IDOR, validasi URL, akses lintas akun, secret scanning, dan akses artifact private.     |
| AI evaluation    | Kualitas ekstraksi skill, akurasi evidence, konsistensi normalisasi, hallucination pada JD, dan keterjelasan alasan matching. |
| Usability test   | Apakah kandidat memahami cara memilih repository dan memeriksa evidence; apakah employer dapat meninjau JD dan kandidat.      |

## 13.3 Evaluasi Kualitas AI

- Gunakan sekumpulan repository contoh dengan teknologi dan peran yang telah diketahui untuk memeriksa apakah AI menemukan skill yang relevan.

- Periksa apakah setiap skill yang diklaim didukung oleh bukti yang benar-benar ada di artifact.

- Catat false positive, false negative, dan skill yang hanya disimpulkan secara tidak langsung.

- Periksa apakah AI membedakan teknologi yang tercantum pada dependency dengan teknologi yang benar-benar digunakan dalam source code.

- Bandingkan JD awal dari AI dengan hasil revisi employer untuk mengetahui bagian yang sering perlu diperbaiki.

- Gunakan penilaian reviewer manusia terhadap relevance matching; jangan mengevaluasi hanya berdasarkan skor model.

# 14. Tahapan Implementasi, Risiko, dan Asumsi

## 14.1 Urutan Implementasi yang Direkomendasikan

| **Tahap**                   | **Pekerjaan**                                                                                         | **Ketergantungan / hasil**                                    |
|-----------------------------|-------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| 1\. Fondasi data            | Finalisasi MySQL schema; SQLAlchemy models; Alembic migration; seed master skill.                     | Tabel dan relasi siap dipakai backend.                        |
| 2\. Core account dan profil | Registrasi/login, role guard, candidate_profile, company_profile.                                     | Candidate dan employer dapat mengakses dashboard sesuai role. |
| 3\. Smart Artifact + GitHub | GitHub OAuth, daftar public repository, repository selection, pembuatan artifact, contribution input. | Repository dapat diimpor sebagai artifact tanpa tabel baru.   |
| 4\. AI Artifact Analysis    | Ingestion, filtering, LangGraph workflow, skill normalization, evidence generation, candidate review. | Artifact menghasilkan skill evidence yang dapat ditinjau.     |
| 5\. Smart Job Descriptor    | Business problem form, JD generation, skill extraction, employer review, publish.                     | Lowongan terstruktur tersedia untuk matching.                 |
| 6\. Matching dan swipe      | Scoring service, explanation, candidate/employer decisions, status mutual.                            | Alur inti JobX dapat ditunjukkan end-to-end.                  |
| 7\. Seeder dan demo         | Data kandidat, artifact, skill evidence, employer, lowongan, dan match yang terkendali.               | Skenario demo konsisten dan dapat diulang.                    |

## 14.2 Prioritas Demo Hackathon

> **SKENARIO DEMO UTAMA**  
> Employer memasukkan kebutuhan sistem inventaris dan memperoleh draft JD Backend Engineer. Kandidat menghubungkan GitHub, memilih repository project, menjelaskan kontribusi sebagai Backend Developer, lalu JobX menganalisis repository untuk menemukan skill seperti Python, FastAPI, MySQL, dan REST API. Matching engine menampilkan kandidat dengan evidence yang dapat dibuka. Kedua pihak melakukan accept sehingga status menjadi mutually_accepted.

Nama skill pada skenario di atas adalah contoh data demo, bukan hasil analisis aktual atas repository tertentu. Seeder harus menyediakan artifact dan evidence yang konsisten agar juri dapat menguji alur secara berulang.

## 14.3 Risiko Produk dan Mitigasi

| **ID** | **Risiko**                                                                   | **Mitigasi**                                                                                                                |
|--------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| R-01   | AI salah mengidentifikasi skill atau menghasilkan klaim yang tidak didukung. | Simpan evidence excerpt/lokasi; bedakan direct dan inferred; review kandidat; uji dengan repository yang telah diketahui.   |
| R-02   | Repository tidak mewakili kontribusi individu.                               | Wajibkan role dan deskripsi kontribusi; jangan menyamakan akses/ownership dengan authorship; tampilkan status klaim.        |
| R-03   | Repository berisi secret atau data sensitif.                                 | Filter file dan secret pattern; jangan kirim file sensitif ke model; sediakan mekanisme penghapusan dan pelaporan.          |
| R-04   | Prompt injection pada README atau source code.                               | Perlakukan isi repository sebagai input tidak tepercaya; isolasi data dari system instruction; validasi output terstruktur. |
| R-05   | Bias pada rekomendasi.                                                       | Jangan gunakan atribut sensitif yang tidak relevan; jelaskan alasan; lakukan review manusia dan evaluasi hasil.             |
| R-06   | Employer memasukkan business problem yang terlalu umum.                      | Minta informasi minimum; tampilkan asumsi; izinkan employer mengedit dan melengkapi draft.                                  |
| R-07   | Cold-start karena kandidat/lowongan sedikit.                                 | Mulai dengan satu segmen pekerjaan; gunakan data demo sintetis yang diberi label; cari employer/kandidat pilot.             |
| R-08   | GitHub API rate limit atau repository tidak tersedia.                        | Gunakan pagination; tangani 403/404/429; retry dengan backoff yang wajar; tampilkan pesan yang jelas.                       |
| R-09   | Skor matching disalahartikan sebagai peluang diterima.                       | Labeli sebagai skor relevansi berbasis data JobX; tampilkan breakdown; nyatakan keterbatasan dan peran keputusan manusia.   |
| R-10   | Data pribadi atau artifact dibagikan terlalu luas.                           | Default visibility yang sesuai; kontrol akses server-side; transparansi pemrosesan; penghapusan sesuai kebijakan.           |

## 14.4 Asumsi dan Ketergantungan

- JobX memiliki lingkungan deployment backend yang dapat menyimpan GitHub OAuth Client ID dan Client Secret secara aman.

- Pengguna yang melakukan impor telah memiliki akun JobX dan mengotorisasi GitHub melalui alur yang disediakan.

- Repository yang diimpor melalui integrasi MVP adalah repository publik yang dimiliki akun GitHub terhubung.

- Kandidat bersedia memberikan konteks role dan kontribusi untuk artifact yang diunggah.

- Employer bersedia meninjau dan menyetujui JD yang dihasilkan AI sebelum lowongan dipublikasikan.

- Tim memiliki akses ke model AI dan layanan yang dibutuhkan untuk menjalankan workflow analisis.

## 14.5 Hal yang Belum Diputuskan

| **Topik**                        | **Keputusan yang masih perlu ditetapkan**                                                                                   |
|----------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| Batas analisis repository        | Maksimum ukuran, jumlah file, kedalaman direktori, bahasa/ekstensi yang dianalisis, dan timeout.                            |
| Model AI                         | Provider, model, batas token, biaya, dan kebijakan penyimpanan data provider.                                               |
| Formula matching                 | Bobot final, perlakuan evidence yang hanya ai_suggested, ambang rekomendasi, dan cara normalisasi saat data tidak tersedia. |
| Format artifact non-GitHub       | Format file yang benar-benar dapat diproses pada versi hackathon.                                                           |
| Retensi data                     | Durasi penyimpanan salinan file, raw_result, dan log analisis.                                                              |
| Kebijakan moderasi dan pelaporan | Prosedur pelaporan artifact palsu, konten berbahaya, atau penyalahgunaan platform.                                          |

# 15. Glosarium dan Referensi

## 15.1 Glosarium

| **Istilah**          | **Definisi dalam konteks JobX**                                                                                                |
|----------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Artifact             | Hasil pekerjaan atau project yang diserahkan kandidat sebagai sumber informasi untuk analisis kompetensi.                      |
| Skill evidence       | Bukti yang ditemukan pada artifact dan dikaitkan dengan suatu keterampilan.                                                    |
| Direct evidence      | Bukti yang secara langsung menunjukkan penggunaan teknologi atau kompetensi.                                                   |
| Inferred evidence    | Bukti yang menunjukkan keterampilan melalui inferensi dari struktur atau karakteristik artifact.                               |
| Confidence score     | Skor keyakinan model terhadap hasil identifikasi; bukan probabilitas penguasaan skill.                                         |
| Business problem     | Deskripsi masalah bisnis atau kebutuhan yang ingin diselesaikan melalui suatu posisi pekerjaan.                                |
| Smart Job Descriptor | Fitur AI yang mengubah business problem menjadi draft Job Description dan kebutuhan skill.                                     |
| Matching score       | Skor relevansi kandidat terhadap lowongan berdasarkan kriteria yang ditetapkan JobX.                                           |
| Mutual acceptance    | Kondisi ketika kandidat dan employer sama-sama menerima rekomendasi yang sama.                                                 |
| OAuth                | Mekanisme otorisasi yang memungkinkan aplikasi memperoleh akses terbatas atas identitas/informasi sesuai persetujuan pengguna. |
| GitHub REST API      | Antarmuka GitHub untuk mengakses informasi akun dan repository secara terprogram.                                              |

## 15.2 Referensi

**\[1\] Pusat Pasar Kerja, Kementerian Ketenagakerjaan Republik Indonesia.** Pasker ID — Highlight Pasar Kerja dan statistik Karirhub/JOSS. Data yang dirujuk: status aktif per 1 Oktober 2026 serta agregat lowongan/lamaran pada periode yang tercantum.

> [https://paskerid.kemnaker.go.id/](https://paskerid.kemnaker.go.id/)

**\[2\] Badan Pusat Statistik.** Tingkat Pengangguran Terbuka Berdasarkan Tingkat Pendidikan, 2025. Terakhir diperbarui 30 Januari 2026.

> [https://www.bps.go.id/id/statistics-table/2/MTE3OSMy/tingkat-pengangguran-terbuka-%E2%80%8Eberdasarkan-tingkat-pendidikan.html](https://www.bps.go.id/id/statistics-table/2/MTE3OSMy/tingkat-pengangguran-terbuka-%E2%80%8Eberdasarkan-tingkat-pendidikan.html)

**\[3\] OECD.** A Skills-First Labour Market (2026), bagian “Promoting skills-first hiring and talent management”. Digunakan sebagai landasan pendekatan keterampilan yang ditunjukkan dan asesmen kompetensi.

> [https://www.oecd.org/en/publications/a-skills-first-labour-market_2e1b85f0-en/full-report/promoting-skills-first-hiring-and-talent-management_81392a48.html](https://www.oecd.org/en/publications/a-skills-first-labour-market_2e1b85f0-en/full-report/promoting-skills-first-hiring-and-talent-management_81392a48.html)

**\[4\] Government Digital Service / Department for Science, Innovation and Technology, United Kingdom.** Responsible AI in Recruitment Guide. Diterbitkan 29 Januari 2025. Digunakan sebagai rujukan risiko bias, transparansi, dan assurance AI rekrutmen.

> [https://www.gov.uk/data-ethics-guidance/responsible-ai-in-recruitment-guide](https://www.gov.uk/data-ethics-guidance/responsible-ai-in-recruitment-guide)

**\[5\] GitHub.** REST API endpoints for repositories — List repositories for a user. Dokumentasi endpoint untuk daftar repository publik, parameter type, sort, per_page, dan page.

> [https://docs.github.com/en/rest/repos/repos](https://docs.github.com/en/rest/repos/repos)

**\[6\] GitHub.** Scopes for OAuth apps. Dokumentasi cakupan akses OAuth, termasuk akses informasi publik tanpa scope dan izin luas pada scope repo.

> [https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps)

**\[7\] Republik Indonesia.** Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi.

> [https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022](https://peraturan.bpk.go.id/Details/229798/uu-no-27-tahun-2022)

**\[8\] GitHub.** REST API endpoints for users — Get the authenticated user. Dokumentasi respons profil publik untuk token OAuth tanpa scope dan informasi profil privat yang memerlukan read:user.

> [https://docs.github.com/en/rest/users/users](https://docs.github.com/en/rest/users/users)

Tanggal akses referensi daring: 14 November 2026. Data pasar kerja dan literatur eksternal digunakan sebagai konteks serta dasar perancangan, bukan sebagai bukti bahwa JobX telah terbukti meningkatkan peluang kerja. Klaim efektivitas produk harus diuji melalui pilot dan evaluasi pengguna.

# Lampiran A. Contoh Output Analisis Artifact

Struktur berikut merupakan contoh konseptual untuk menunjukkan jenis informasi yang diharapkan. Angka confidence dan nama skill adalah ilustrasi, bukan hasil pengujian model.

```json
{
  "artifact_title": "Hospital Management System",
  "candidate_role": "Backend Developer",
  "summary": "Aplikasi untuk mengelola data pasien, jadwal, dan administrasi rumah sakit.",
  "skills": [
    {
      "canonical_skill": "FastAPI",
      "evidence_kind": "direct",
      "confidence_score": 0.92,
      "evidence_excerpt": "FastAPI application and route definitions",
      "evidence_location": "backend/app/main.py",
      "review_status": "ai_suggested"
    },
    {
      "canonical_skill": "MySQL",
      "evidence_kind": "direct",
      "confidence_score": 0.88,
      "evidence_excerpt": "Database connection and SQL query usage",
      "evidence_location": "backend/app/database.py",
      "review_status": "ai_suggested"
    }
  ],
  "limitations": [
    "The repository does not independently verify individual authorship."
  ]
}
```

# Lampiran B. Contoh Skenario Demo End-to-End

| **Aktor**             | **Tindakan**                                                                                            | **Hasil yang terlihat**                                                       |
|-----------------------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| Kandidat              | Menghubungkan GitHub, memilih repository publik, lalu mengisi role Backend Developer dan kontribusinya. | Artifact tercatat dengan source_url GitHub dan metadata repository.           |
| JobX AI               | Menganalisis README, struktur, konfigurasi, dan source code terpilih.                                   | Skill evidence muncul beserta excerpt/lokasi, confidence, dan jenis evidence. |
| Employer              | Mengisi business problem untuk pengembangan sistem inventaris.                                          | Draft Job Description beserta must-have dan preferred skills.                 |
| JobX Matching         | Membandingkan requirement pekerjaan dengan skill evidence kandidat.                                     | Skor, rincian, serta penjelasan kecocokan ditampilkan.                        |
| Kandidat dan employer | Keduanya memilih accept.                                                                                | job_match berubah menjadi mutually_accepted.                                  |
