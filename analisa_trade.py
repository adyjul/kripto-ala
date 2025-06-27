# analyze_validation.py

import pandas as pd

log_file = 'logs/validation_log.csv'

try:
    df = pd.read_csv(log_file)
except FileNotFoundError:
    print("❌ File log belum ditemukan.")
    exit()

if df.empty:
    print("❌ Log masih kosong.")
    exit()

total = len(df)
tp = df['tp_hit'].sum()
sl = df['sl_hit'].sum()
hold = df[df['decision'] == 'HOLD'].shape[0]
no_hit = df[(df['result'] == 'NO-HIT')].shape[0]

winrate = (tp / (tp + sl)) * 100 if (tp + sl) > 0 else 0
rrr = (df['tp_hit'].sum() * 0.002) / (df['sl_hit'].sum() * 0.001) if df['sl_hit'].sum() > 0 else "∞"

print(f"🔍 Evaluasi Hasil Validasi:")
print(f"Total Data       : {total}")
print(f"Total LONG/SHORT : {total - hold}")
print(f"TP Hit           : {tp}")
print(f"SL Hit           : {sl}")
print(f"NO-HIT           : {no_hit}")
print(f"HOLD             : {hold}")
print(f"✅ Winrate        : {winrate:.2f}%")
print(f"📈 Estimasi RRR   : {rrr}")
