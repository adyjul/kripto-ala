import pandas as pd

# Baca log validasi
df = pd.read_csv('logs/validation_log.csv')

# Hitung selisih prediksi dengan harga sekarang dalam persen
df['delta_pct'] = (df['predicted_price'] - df['current_price']) / df['current_price']

# Tampilkan ringkasan statistik
print("📊 Analisis Delta (%) antara Prediksi dan Harga Sekarang:\n")
print(df['delta_pct'].describe())

# Tambahkan contoh nilai ekstrem
print("\n📈 Nilai-nilai terbesar (LONG signal candidates):")
print(df.sort_values('delta_pct', ascending=False).head(5)[['current_price', 'predicted_price', 'delta_pct']])

print("\n📉 Nilai-nilai terkecil (SHORT signal candidates):")
print(df.sort_values('delta_pct').head(5)[['current_price', 'predicted_price', 'delta_pct']])
