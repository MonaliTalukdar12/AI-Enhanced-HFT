import socket
import numpy as np
import joblib
import traceback
import warnings
import sys

warnings.filterwarnings("ignore", category=UserWarning)

print("Inizio script")

# === Parametri
n_features = 17
host = '127.0.0.1'
port = 0000

def preprocess_input(data_str):
    values = list(map(float, data_str.strip().split()))
    if len(values) != n_features:
        raise ValueError("Lunghezza input errata")
    x = np.array(values).reshape(1, -1)
    x_scaled = scaler.transform(x)
    return x_scaled

try:
    print("Caricamento scaler...")
    scaler = joblib.load("XGBoost/scaler_xgboost.save")
    print("Scaler caricato.")

    print("Caricamento modello XGBoost...")
    model = joblib.load("XGBoost/xgboost_trend_model.pkl")
    print("Modello caricato.")

    # === Server TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)
        s.settimeout(1.0)

        print(f"Model Server in ascolto su {host}:{port} — premi Ctrl+C per uscire")

        while True:
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print("\nInterruzione da tastiera — chiusura server...")
                break

            with conn:
                print("Connessione da:", addr)
                try:
                    data = conn.recv(10000)
                    decoded = data.decode("utf-8")

                    if decoded.strip() == "PING":
                        print("Handshake ricevuto: PING")
                        conn.send(b"0")
                        continue

                    print("📨 Messaggio ricevuto:", decoded[:100] + "..." if len(decoded) > 100 else decoded)

                    x_input = preprocess_input(decoded)
                    pred = model.predict(x_input)
                    label = -1 if pred[0] == 0 else 1
                    print(f"Predizione classe: {pred[0]} → tradotto: {label}")

                    conn.send(str(label).encode("utf-8"))
                    print("Risposta inviata al client\n")

                except Exception as e:
                    print("Errore nella gestione del messaggio:", e)
                    traceback.print_exc()
                    conn.send(b"0")

except KeyboardInterrupt:
    print("\nServer interrotto manualmente (Ctrl+C) — uscita pulita.")
    sys.exit(0)

except Exception as e:
    print("Errore all'avvio del server:")
    traceback.print_exc()
