import pandas as pd
from datetime import datetime

FILENAME = 'validasi_scalping_15m.xlsx'
OUTPUT_XLSX = 'analisa_scalping_15m.xlsx'
RRR = 2.0  # Risk:Reward Ratio

def analisa():
    try:
        df = pd.read_excel(FILENAME)
    except Exception as e:
        print(f"❌ Gagal membaca file: {e}")
        return

    total_data = len(df)
    df_trades = df[df['status'].isin(['TP', 'SL', 'NO-HIT'])]
    total_trade = len(df_trades)

    total_tp = len(df_trades[df_trades['status'] == 'TP'])
    total_sl = len(df_trades[df_trades['status'] == 'SL'])
    total_nohit = len(df_trades[df_trades['status'] == 'NO-HIT'])
    total_hold = len(df[df['status'] == 'HOLD'])

    winrate = (total_tp / (total_tp + total_sl)) * 100 if (total_tp + total_sl) > 0 else 0
    pnl = (total_tp * RRR) - total_sl

    # Output ke terminal
    print(f"""
📊 Analisa Trade 15M Scalping dari XLSX
----------------------------------------
📁 Total Data     : {total_data}
📈 Total Trade    : {total_trade}
  ✅ TP           : {total_tp}
  ❌ SL           : {total_sl}
  ⚠️  NO-HIT       : {total_nohit}
  ⏳ HOLD         : {total_hold}

🎯 Winrate        : {winrate:.2f}%
💰 Estimasi PnL   : {pnl:.2f} unit (RRR={RRR})
""")

    # Simpan hasil analisa (opsional)
    summary_data = {
        'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'total_data': [total_data],
        'total_trade': [total_trade],
        'tp': [total_tp],
        'sl': [total_sl],
        'no_hit': [total_nohit],
        'hold': [total_hold],
        'winrate(%)': [winrate],
        'estimasi_pnl': [pnl]
    }

    df_summary = pd.DataFrame(summary_data)
    df_summary.to_excel(OUTPUT_XLSX, index=False)
    print(f"✅ Ringkasan disimpan ke: {OUTPUT_XLSX}")

if __name__ == "__main__":
    analisa()
