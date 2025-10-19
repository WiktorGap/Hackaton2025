import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle

# ============================================
# KONFIGURACJA ŚCIEŻEK
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model_ludnosc_plock.pkl')
CSV_PATH = os.path.join(BASE_DIR, 'predykcje_ludnosc_2024_2030.csv')

print("============================================")
print("AKTUALNY KATALOG ROBOCZY:")
print(BASE_DIR)
print("============================================\n")

# ============================================
# KROK 1: Wczytanie danych
# ============================================
print("Wczytywanie danych...")

data = {
    'Lata': [1950, 1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990, 1995, 1996, 1997, 1998, 1999,
             2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
             2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
    'Ludnosc_ogolem': [33128, 37015, 42798, 54952, 72336, 87827, 102548, 114744, 123398, 127174,
                       127670, 130596, 131011, 128654, 128580, 128359, 128208, 128145, 127841,
                       127461, 127224, 126968, 126709, 126542, 124691, 124318, 123627, 122815,
                       122224, 121731, 121295, 120787, 120000, 119425, 114974, 113660, 112483, 111190],
    'Malzenstwa': [325, 355, 340, 406, 563, 743, 882, 932, 828, 727, 700, 757, 680, 804, 834, 755,
                   699, 737, 729, 735, 824, 885, 875, 833, 769, 667, 700, 577, 609, 553, 604, 555,
                   534, 528, 421, 470, 452, 448],
    'Urodzenia_zywe': [953, 955, 764, 901, 1171, 1598, 1848, 1881, 1512, 1329, 1354, 1321, 1194, 1166,
                       1202, 1105, 1092, 1188, 1137, 1188, 1298, 1249, 1375, 1380, 1286, 1231, 1285,
                       1128, 1146, 1101, 1167, 1115, 1095, 1079, 966, 840, 811, 654],
    'Zgony_ogolem': [388, 386, 317, 365, 491, 619, 725, 867, 941, 948, 962, 1014, 880, 1113, 1053, 967,
                     1052, 1002, 1027, 1041, 1149, 1172, 1180, 1189, 1182, 1116, 1265, 1191, 1220, 1209,
                     1259, 1265, 1360, 1327, 1667, 1694, 1487, 1394],
    'Przyrost_naturalny': [565, 569, 447, 536, 680, 979, 1123, 1014, 571, 381, 392, 307, 314, -53, 149,
                           138, -15, 186, 110, 147, 149, 62, 195, 191, 104, 115, 20, -63, -74, -108, -92,
                           -150, -265, -248, -701, -854, -676, -740],
    'Ogolne_saldo_migracji': [1015, 2997, 2195, 1970, 2262, 2185, 1579, 672, 831, 448, 555, 205, 110, -25,
                              -162, -56, -152, -326, -635, -557, -483, -621, -499, -399, -585, -488, -516,
                              -550, -475, -503, -354, -353, -393, -402, -295, -531, -447, -471]
}

df = pd.DataFrame(data)
print(f"✓ Wczytano {len(df)} wierszy danych")

# ============================================
# KROK 2: Feature Engineering
# ============================================
print("\nTworzenie dodatkowych cech...")

df['Lata_od_1950'] = df['Lata'] - 1950
df['Trend'] = range(len(df))
df['Urodzenia_na_1000'] = (df['Urodzenia_zywe'] / df['Ludnosc_ogolem']) * 1000
df['Zgony_na_1000'] = (df['Zgony_ogolem'] / df['Ludnosc_ogolem']) * 1000
df['Bilans_naturalny'] = df['Urodzenia_zywe'] - df['Zgony_ogolem']

print(f"✓ Utworzono {len(df.columns)} cech")

# ============================================
# KROK 3: Przygotowanie danych
# ============================================
print("\nPrzygotowanie danych...")

feature_columns = ['Lata_od_1950', 'Trend', 'Malzenstwa', 'Urodzenia_zywe',
                   'Zgony_ogolem', 'Przyrost_naturalny', 'Ogolne_saldo_migracji']
target_column = 'Ludnosc_ogolem'

X = df[feature_columns]
y = df[target_column]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=False
)

print(f"✓ Zbiór treningowy: {len(X_train)} próbek")
print(f"✓ Zbiór testowy: {len(X_test)} próbek")

# ============================================
# KROK 4: Normalizacja danych
# ============================================
print("\nNormalizacja danych...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("✓ Dane znormalizowane")

# ============================================
# KROK 5: Trenowanie modeli
# ============================================
print("\nTrenowanie modeli...")

models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42, max_depth=3)
}

results = {}

for name, model in models.items():
    print(f"\n--- {name} ---")
    model.fit(X_train_scaled, y_train)
    y_pred_test = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2 = r2_score(y_test, y_pred_test)
    results[name] = {'model': model, 'mae': mae, 'rmse': rmse, 'r2': r2}
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R² score: {r2:.4f}")

# ============================================
# KROK 6: Wybór najlepszego modelu
# ============================================
print("\n" + "="*50)
print("PODSUMOWANIE WYNIKÓW")
print("="*50)

best_model_name = min(results, key=lambda x: results[x]['mae'])
best_model = results[best_model_name]['model']

print(f"\nNajlepszy model: {best_model_name}")
print(f"MAE: {results[best_model_name]['mae']:.2f}")
print(f"RMSE: {results[best_model_name]['rmse']:.2f}")
print(f"R²: {results[best_model_name]['r2']:.4f}")

# ============================================
# KROK 7: Zapis modelu i scaler'a
# ============================================
print("\n" + "="*50)
print("EKSPORT MODELU")
print("="*50)

model_package = {
    'model': best_model,
    'scaler': scaler,
    'feature_columns': feature_columns,
    'target_column': target_column,
    'model_name': best_model_name,
    'metrics': results[best_model_name]
}

with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model_package, f)

print(f"✓ Model zapisany do: {MODEL_PATH}")

# ============================================
# KROK 8: Predykcja przyszłych wartości
# ============================================
print("\n" + "="*50)
print("PRZYKŁAD WCZYTANIA I UŻYCIA MODELU")
print("="*50)

with open(MODEL_PATH, 'rb') as f:
    loaded_package = pickle.load(f)

loaded_model = loaded_package['model']
loaded_scaler = loaded_package['scaler']
loaded_features = loaded_package['feature_columns']

print(f"✓ Wczytano model: {loaded_package['model_name']}")

future_years = range(2024, 2031)
predictions_future = []

print("\nPredykcje ludności dla lat 2024-2030:")
print("-" * 50)

for year in future_years:
    year_data = {
        'Lata_od_1950': year - 1950,
        'Trend': len(df) + (year - 2024),
        'Malzenstwa': 430,
        'Urodzenia_zywe': 620 - (year - 2024) * 10,
        'Zgony_ogolem': 1400 + (year - 2024) * 5,
        'Przyrost_naturalny': -780 - (year - 2024) * 20,
        'Ogolne_saldo_migracji': -480
    }
    X_future = pd.DataFrame([year_data])[loaded_features]
    X_future_scaled = loaded_scaler.transform(X_future)
    prediction = loaded_model.predict(X_future_scaled)[0]
    predictions_future.append(prediction)
    print(f"{year}: {prediction:,.0f} mieszkańców")

predictions_df = pd.DataFrame({'Rok': list(future_years), 'Przewidywana_ludnosc': predictions_future})
predictions_df.to_csv(CSV_PATH, index=False)

print(f"\n✓ Predykcje zapisane do: {CSV_PATH}")
print("\n" + "="*50)
print("GOTOWE!")
print("="*50)
print("\nPliki utworzone:")
print(f"1. {MODEL_PATH}")
print(f"2. {CSV_PATH}")
