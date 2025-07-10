import pandas as pd
import numpy as np
import joblib
import xgboost as xgb

# === Caricamento dati
df = pd.read_csv("xgboost_ready_dataset.csv", parse_dates=['Time'])

# === Carica scaler e modello
scaler = joblib.load("scaler_xgboost.save")
model = joblib.load("xgboost_trend_model.pkl")

# === Colonne usate per la predizione
features = [
    'Open', 'High', 'Low', 'Close', 'Volume',
    'EMA_Fast', 'EMA_Slow', 'ADX', 'EMA_diff',
    'Close_pct_change', 'Volume_pct_change',
    'ADX_delta', 'Volume_delta',
    'ADX_roll_std3', 'Volume_roll_std3'
]

# === Preprocessing
X_scaled = scaler.transform(df[features])
timestamps = df['Time'].values

# === Previsione
y_pred_raw = model.predict(X_scaled)

# Converti 0 → -1 per mantenere compatibilità con l’EA
trend_pred = np.where(y_pred_raw == 1, 1, -1)

# === Costruzione DataFrame finale
df_out = pd.DataFrame({
    'time': timestamps,
    'trend': trend_pred
})

# === Salvataggio CSV
df_out.sort_values("time", ascending=True).to_csv("trend_forecast_XGBoost.csv", index=False)
print("Previsioni salvate in trend_forecast_XGBoost.csv")
