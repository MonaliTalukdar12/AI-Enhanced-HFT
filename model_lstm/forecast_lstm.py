import pandas as pd
import numpy as np
import joblib
import tensorflow as tf

# === Caricamento dati
df = pd.read_csv("lstm_ready_dataset.csv", parse_dates=['Time'])

# === Parametri
sequence_length = 20
features = [
    'Open', 'High', 'Low', 'Close', 'Volume',
    'EMA_Fast', 'EMA_Slow', 'ADX', 'EMA_diff',
    'Close_pct_change', 'Volume_pct_change',
    'ADX_delta', 'Volume_delta',
    'ADX_roll_std3', 'Volume_roll_std3'
]

# === Preprocessing
scaler = joblib.load("scaler_lstm.save")
X_scaled = scaler.transform(df[features])
y_raw = df['trend'].values
timestamps = df['Time'].values

# === Costruzione sequenze
X_seq, y_seq, t_seq = [], [], []
for i in range(len(X_scaled) - sequence_length):
    X_seq.append(X_scaled[i:i+sequence_length])
    y_seq.append(y_raw[i+sequence_length])
    t_seq.append(timestamps[i+sequence_length])

X_seq = np.array(X_seq)

# === Carica modello
model = tf.keras.models.load_model("lstm_trend_model.h5")

# === Previsione
y_pred = model.predict(X_seq, verbose=0).flatten()
trend_pred = np.where(y_pred > 0, 1, -1)  # soglia per classificazione binaria

# === Salvataggio CSV per MQL5
df_out = pd.DataFrame({
    'time': t_seq,
    'trend': trend_pred
})

df_out.sort_values("time", ascending=True).to_csv("trend_forecast_lstm.csv", index=False)
print("Previsioni salvate in trend_forecast_lstm.csv")
