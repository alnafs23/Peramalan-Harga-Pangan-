"""
Analisis Peramalan Harga Sembako & Korelasi dengan Statistik Fintech P2P Lending (OJK)
Script ini menghasilkan seluruh chart yang dipakai di README dan dashboard.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error

plt.rcParams['figure.figsize'] = (11, 5)
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
sns.set_palette("Set2")

FIG_DIR = "../outputs/figures"

# ---------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------
df = pd.read_csv("../data/master_dataset.csv")

bulan_order = ['Januari','Februari','Maret','April','Mei','Juni','Juli',
               'Agustus','September','Oktober','November','Desember']
df['periode'] = pd.Categorical(df['bulan'], categories=bulan_order, ordered=True)
df['bulan_num'] = df['periode'].cat.codes + 1
df['tanggal'] = pd.to_datetime(df['tahun'].astype(str) + '-' + df['bulan_num'].astype(str) + '-01')
df = df.sort_values('tanggal').reset_index(drop=True)

komoditas_cols = ['beras_premium','beras_medium','bawang_merah','bawang_putih',
                   'cabai_merah_keriting','cabai_rawit_merah','daging_sapi',
                   'daging_ayam','telur_ayam','gula_pasir','minyak_goreng_kemasan']

ojk_cols = ['ojk_tkb90','ojk_twp90','ojk_roa','ojk_roe','ojk_bopo','ojk_penyaluran_pertanian_miliar']

print("Jumlah baris:", len(df))
print(df[['tahun','bulan'] + komoditas_cols].head())

# ---------------------------------------------------------------
# 2. EDA - TREN HARGA PER KOMODITAS
# ---------------------------------------------------------------
label_map = {
    'beras_premium':'Beras Premium','beras_medium':'Beras Medium','bawang_merah':'Bawang Merah',
    'bawang_putih':'Bawang Putih','cabai_merah_keriting':'Cabai Merah Keriting',
    'cabai_rawit_merah':'Cabai Rawit Merah','daging_sapi':'Daging Sapi','daging_ayam':'Daging Ayam',
    'telur_ayam':'Telur Ayam','gula_pasir':'Gula Pasir','minyak_goreng_kemasan':'Minyak Goreng Kemasan'
}

fig, axes = plt.subplots(4, 3, figsize=(16, 14))
axes = axes.flatten()
for i, col in enumerate(komoditas_cols):
    axes[i].plot(df['tanggal'], df[col], marker='o', markersize=3, linewidth=1.5)
    axes[i].set_title(label_map[col], fontsize=11, fontweight='bold')
    axes[i].tick_params(axis='x', rotation=45, labelsize=8)
    axes[i].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
axes[-1].axis('off')
plt.suptitle('Tren Harga Komoditas Pangan Nasional, Jan 2024 - Des 2025', fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/01_tren_harga_semua_komoditas.png", dpi=140, bbox_inches='tight')
plt.close()
print("Saved: 01_tren_harga_semua_komoditas.png")

# ---------------------------------------------------------------
# 3. VOLATILITAS (Coefficient of Variation)
# ---------------------------------------------------------------
cv = (df[komoditas_cols].std() / df[komoditas_cols].mean() * 100).sort_values(ascending=False)
cv.index = [label_map[c] for c in cv.index]

plt.figure(figsize=(10,6))
bars = plt.barh(cv.index[::-1], cv.values[::-1], color=sns.color_palette("Set2", len(cv)))
plt.xlabel('Coefficient of Variation (%)')
plt.title('Volatilitas Harga Komoditas Pangan (Jan 2024 - Des 2025)\nSemakin tinggi = semakin fluktuatif = risiko kerugian lebih besar', fontweight='bold')
for i, v in enumerate(cv.values[::-1]):
    plt.text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=9)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/02_volatilitas_komoditas.png", dpi=140, bbox_inches='tight')
plt.close()
print("Saved: 02_volatilitas_komoditas.png")
print("\nTop 3 komoditas paling volatil:")
print(cv.head(3))

# ---------------------------------------------------------------
# 4. TREN INDIKATOR OJK
# ---------------------------------------------------------------
fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
axes[0].plot(df['tanggal'], df['ojk_twp90']*100, marker='o', color='crimson', label='TWP90 (%)')
axes[0].set_title('TWP90 - Tingkat Wanprestasi Fintech P2P Lending (%)', fontweight='bold')
axes[0].set_ylabel('%')
axes[0].tick_params(axis='x', rotation=45)

axes[1].plot(df['tanggal'], df['ojk_penyaluran_pertanian_miliar'], marker='o', color='seagreen')
axes[1].set_title('Penyaluran Pinjaman Fintech ke Sektor Pertanian, Kehutanan & Perikanan (Miliar Rp)', fontweight='bold')
axes[1].set_ylabel('Miliar Rp')
axes[1].tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/03_tren_indikator_ojk.png", dpi=140, bbox_inches='tight')
plt.close()
print("Saved: 03_tren_indikator_ojk.png")

# ---------------------------------------------------------------
# 5. KORELASI HARGA vs INDIKATOR OJK (termasuk lag 1 & 2 bulan)
# ---------------------------------------------------------------
corr_records = []
for col in komoditas_cols:
    for ojk_col in ojk_cols:
        for lag in [0, 1, 2]:
            shifted = df[ojk_col].shift(lag)
            valid = shifted.notna()
            if valid.sum() > 5:
                r = np.corrcoef(df.loc[valid, col], shifted[valid])[0,1]
                corr_records.append({'komoditas': label_map[col], 'indikator_ojk': ojk_col, 'lag_bulan': lag, 'korelasi': r})

corr_df = pd.DataFrame(corr_records)
corr_df.to_csv("../outputs/tabel_korelasi_lengkap.csv", index=False)

# Heatmap korelasi kontemporer (lag=0)
pivot0 = corr_df[corr_df['lag_bulan']==0].pivot(index='komoditas', columns='indikator_ojk', values='korelasi')
plt.figure(figsize=(9,7))
sns.heatmap(pivot0, annot=True, fmt='.2f', cmap='RdBu_r', center=0, vmin=-1, vmax=1, cbar_kws={'label':'Korelasi Pearson'})
plt.title('Korelasi Harga Pangan vs Indikator OJK (tanpa lag)', fontweight='bold')
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/04_heatmap_korelasi.png", dpi=140, bbox_inches='tight')
plt.close()
print("Saved: 04_heatmap_korelasi.png")

# Korelasi terkuat (any lag) untuk highlight temuan
strongest = corr_df.reindex(corr_df['korelasi'].abs().sort_values(ascending=False).index).head(10)
print("\nTop 10 korelasi terkuat (harga vs OJK, termasuk lag):")
print(strongest.to_string(index=False))

# ---------------------------------------------------------------
# 6. FORECASTING - Linear Regression w/ Trend + Seasonal Dummy
#    Dievaluasi untuk 2 komoditas paling volatil
# ---------------------------------------------------------------
target_commodities = cv.index[:2].tolist()  # 2 paling volatil (label sudah di-map)
reverse_label = {v:k for k,v in label_map.items()}

forecast_results = []
fig, axes = plt.subplots(1, 2, figsize=(15,5))

for i, target_label in enumerate(target_commodities):
    col = reverse_label[target_label]
    data = df[['tanggal','bulan_num', col]].copy()
    data['t'] = np.arange(len(data))
    month_dummies = pd.get_dummies(data['bulan_num'], prefix='m', drop_first=True)
    X = pd.concat([data[['t']], month_dummies], axis=1)
    y = data[col]

    n_test = 6
    X_train, X_test = X.iloc[:-n_test], X.iloc[-n_test:]
    y_train, y_test = y.iloc[:-n_test], y.iloc[-n_test:]

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Baseline: naive seasonal (nilai bulan sama tahun lalu) fallback to last value
    naive_pred = y_train.iloc[-n_test:].values if len(y_train) >= n_test else np.repeat(y_train.iloc[-1], n_test)

    mape_model = mean_absolute_percentage_error(y_test, y_pred) * 100
    rmse_model = np.sqrt(mean_squared_error(y_test, y_pred))
    mape_naive = mean_absolute_percentage_error(y_test, naive_pred) * 100
    rmse_naive = np.sqrt(mean_squared_error(y_test, naive_pred))

    forecast_results.append({
        'komoditas': target_label, 'MAPE_model_%': round(mape_model,2), 'RMSE_model': round(rmse_model,1),
        'MAPE_naive_%': round(mape_naive,2), 'RMSE_naive': round(rmse_naive,1)
    })

    axes[i].plot(data['tanggal'], y, label='Aktual', marker='o', markersize=3, color='black')
    axes[i].plot(data['tanggal'].iloc[-n_test:], y_pred, label='Prediksi (Model)', marker='s', linestyle='--', color='crimson')
    axes[i].axvline(data['tanggal'].iloc[-n_test], color='gray', linestyle=':', alpha=0.7)
    axes[i].set_title(f'Forecast: {target_label}', fontweight='bold')
    axes[i].legend(fontsize=9)
    axes[i].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/05_hasil_forecasting.png", dpi=140, bbox_inches='tight')
plt.close()
print("Saved: 05_hasil_forecasting.png")

forecast_df = pd.DataFrame(forecast_results)
forecast_df.to_csv("../outputs/tabel_evaluasi_model.csv", index=False)
print("\nHasil evaluasi model:")
print(forecast_df.to_string(index=False))

print("\n=== SELESAI - semua chart tersimpan di outputs/figures/ ===")
