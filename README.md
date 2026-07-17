# Peramalan Harga Sembako & Korelasi dengan Statistik Fintech P2P Lending (OJK)

Proyek analisis data untuk memahami tren dan volatilitas harga komoditas pangan pokok nasional, mengeksplorasi
hubungannya dengan kondisi pembiayaan fintech P2P lending, serta membangun model peramalan sederhana sebagai
alat bantu mitigasi risiko kerugian bagi pelaku usaha pangan.

## Latar Belakang

Fluktuasi harga sembako berdampak langsung pada risiko kerugian pelaku usaha dan daya beli masyarakat.
Proyek ini menggabungkan dua sisi yang jarang disandingkan:
- **Sisi harga** — pergerakan harga pangan tingkat konsumen nasional
- **Sisi pembiayaan** — kondisi akses modal lewat fintech P2P lending (LPBBTI), termasuk penyaluran khusus
  ke sektor Pertanian, Kehutanan, dan Perikanan

Tujuan akhirnya dua arah: (1) membantu mitigasi risiko kerugian lewat peramalan harga, dan (2) membuka ruang
eksplorasi bagaimana akses pembiayaan berkaitan dengan stabilitas harga pangan — relevan untuk kesejahteraan
petani dalam jangka panjang.

## Sumber Data

| Data | Sumber | Cakupan |
|---|---|---|
| Harga Pangan Nasional | [Open Data Badan Pangan Nasional](https://data.badanpangan.go.id) | 11 komoditas, bulanan, Jan 2024 - Des 2025 |
| Statistik Fintech P2P Lending (LPBBTI) | [OJK](https://ojk.go.id/id/kanal/iknb/data-dan-statistik/fintech) | TKB90, TWP90, ROA, ROE, BOPO, penyaluran sektor produktif, bulanan, Jan 2024 - Des 2025 |

## Struktur Folder

```
├── data/
│   ├── master_dataset.csv              # dataset gabungan final (dipakai untuk analisis)
│   ├── harga_pangan_nasional.csv       # data harga pangan mentah
│   ├── ojk_kinerja_keuangan.csv        # TKB90, TWP90, ROA, ROE, BOPO
│   └── ojk_sektor_pertanian.csv        # penyaluran pinjaman sektor pertanian & pertambangan
├── notebooks/
│   ├── analisis_peramalan_harga_pangan.ipynb   # notebook utama (EDA -> korelasi -> forecasting)
│   └── run_analysis.py                 # versi script .py dari notebook (untuk otomasi/CI)
├── outputs/
│   ├── figures/                        # semua chart hasil analisis (PNG)
│   ├── tabel_korelasi_lengkap.csv
│   └── tabel_evaluasi_model.csv
├── dashboard/
│   └── index.html                      # dashboard interaktif statis (buka langsung di browser)
├── requirements.txt
└── README.md
```

## Cara Menjalankan

```bash
pip install -r requirements.txt
cd notebooks
jupyter notebook analisis_peramalan_harga_pangan.ipynb
```

Atau jalankan langsung sebagai script:
```bash
cd notebooks
python run_analysis.py
```

Dashboard interaktif bisa dibuka langsung tanpa server — cukup buka `dashboard/index.html` di browser.

## Metodologi

1. **EDA** — tren harga per komoditas, volatilitas (coefficient of variation)
2. **Analisis Korelasi** — korelasi Pearson antara harga pangan dan indikator OJK, termasuk uji lag 1-2 bulan
   untuk eksplorasi potensi *leading indicator*
3. **Peramalan** — Linear Regression dengan trend + dummy musiman bulanan, dievaluasi terhadap baseline naive
   seasonal (MAPE, RMSE)

> **Kenapa bukan SARIMA/Prophet?** Dengan hanya 24 observasi bulanan, model time-series kompleks berisiko
> overfitting dan sulit divalidasi dengan andal. Pendekatan regresi musiman sederhana dipilih agar hasil lebih
> robust dan mudah diinterpretasi untuk kondisi data saat ini. Lihat bagian Pengembangan Lanjutan.

## Temuan Utama

1. **Cabai Rawit Merah** (CV ≈ 20.4%), **Cabai Merah Keriting** (CV ≈ 16.4%), dan **Bawang Merah** (CV ≈ 16.2%)
   adalah tiga komoditas dengan volatilitas harga tertinggi — prioritas utama untuk sistem peringatan dini
   risiko kerugian.
2. Ditemukan korelasi kontemporer yang cukup kuat antara harga **Minyak Goreng Kemasan dan ROA fintech lending
   (r ≈ 0.80)**. Ini kemungkinan besar korelasi tidak langsung (*spurious correlation*) — keduanya sama-sama
   dipengaruhi tren makroekonomi umum sepanjang 2024-2025, bukan indikasi hubungan sebab-akibat langsung.
3. Model regresi musiman **mengungguli baseline naive untuk Cabai Rawit Merah** (MAPE 33.1% vs 43.5%), tetapi
   **kalah dari baseline naive untuk Cabai Merah Keriting** (MAPE 27.3% vs 14.9%) — hasil dilaporkan apa
   adanya untuk menjaga kejujuran evaluasi, bukan dipilih yang terlihat bagus saja.
4. Hubungan data fintech P2P lending dengan harga pangan bersifat **eksploratif/makro**, karena data OJK yang
   tersedia publik bersifat agregat nasional tanpa breakdown sub-sektor pertanian spesifik. Ini adalah
   limitasi data, bukan kesimpulan bahwa hubungannya tidak ada.

## Keterbatasan

- Rentang data terbatas 24 bulan (Jan 2024 - Des 2025) — idealnya time-series forecasting butuh histori
  lebih panjang untuk menangkap pola musiman multi-tahun secara andal
- Data fintech OJK bersifat agregat nasional; belum ada breakdown pinjaman yang spesifik untuk petani sembako
- Korelasi yang ditemukan bersifat eksploratif dan **tidak membuktikan kausalitas**

## Pengembangan Lanjutan

- Perpanjang data historis begitu tersedia, lalu terapkan SARIMA/SARIMAX (`statsmodels`) atau Prophet
- Sandingkan data fintech per provinsi (Tabel 9 OJK) dengan data harga pangan per provinsi untuk analisis
  risiko regional
- Uji Granger causality formal untuk mengevaluasi klaim *leading indicator* secara lebih ketat

## Lisensi Data

Data bersumber dari Open Data Badan Pangan Nasional dan OJK, digunakan untuk keperluan riset/analisis non-komersial.
