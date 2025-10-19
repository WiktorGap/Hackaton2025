from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle
import datetime
import os

app = Flask(__name__)

# ======================================
# 1. Wczytaj model po uruchomieniu serwera
# ======================================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model_ludnosc_plock.pkl")

with open(MODEL_PATH, 'rb') as f:
    model_package = pickle.load(f)


model = model_package['model']
scaler = model_package['scaler']
features = model_package['feature_columns']

# ======================================
# 2. Strona główna (formularz)
# ======================================
@app.route('/')
def index():
    return render_template('index.html')

# ======================================
# 3. Obsługa formularza
# ======================================
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        years_ahead = int(request.form['years'])
    except:
        years_ahead = 5  # domyślnie 5 lat

    current_year = datetime.datetime.now().year
    future_years = range(current_year, current_year + years_ahead + 1)
    predictions = []

    for i, year in enumerate(future_years):
        year_data = {
            'Lata_od_1950': year - 1950,
            'Trend': 38 + i,  # kontynuacja trendu z danych historycznych (1950–2023 = 38 punktów)
            'Malzenstwa': 430,
            'Urodzenia_zywe': 620 - i * 10,
            'Zgony_ogolem': 1400 + i * 5,
            'Przyrost_naturalny': -780 - i * 20,
            'Ogolne_saldo_migracji': -480
        }

        X_future = pd.DataFrame([year_data])[features]
        X_future_scaled = scaler.transform(X_future)
        prediction = model.predict(X_future_scaled)[0]

        predictions.append({
            'rok': year,
            'prognoza': round(prediction)
        })

    return render_template('results.html', predictions=predictions)

# ======================================
# 4. Uruchom serwer
# ======================================
if __name__ == '__main__':
    app.run(debug=True)
