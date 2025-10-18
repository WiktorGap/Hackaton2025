from flask import Flask, render_template, Response
import json
import csv
from io import StringIO
import random

app = Flask(__name__)

# ==============================================================================
# 1. SYMULACJA BAZY DANYCH (MOCK SQL)
# ==============================================================================

# --- DANE DLA STRONY GŁÓWNEJ (DEMOGRAFIA) ---
def get_data_demografia_simulation():
    """Symuluje pobranie danych demograficznych."""
    return [
        {'lata': 1950, 'ludnosc_ogolem': 33128, 'urodzenia_zywe': 953, 'zgony_ogolem': 388, 'przyrost_naturalny_na_1000': 17.0, 'saldo_migracji': 1015},
        {'lata': 1965, 'ludnosc_ogolem': 54952, 'urodzenia_zywe': 901, 'zgony_ogolem': 365, 'przyrost_naturalny_na_1000': 10.0, 'saldo_migracji': 1970},
        {'lata': 1980, 'ludnosc_ogolem': 102548, 'urodzenia_zywe': 1848, 'zgony_ogolem': 725, 'przyrost_naturalny_na_1000': 11.1, 'saldo_migracji': 1579},
        {'lata': 1995, 'ludnosc_ogolem': 127174, 'urodzenia_zywe': 1329, 'zgony_ogolem': 948, 'przyrost_naturalny_na_1000': 3.0, 'saldo_migracji': 448},
        {'lata': 2005, 'ludnosc_ogolem': 127461, 'urodzenia_zywe': 1188, 'zgony_ogolem': 1041, 'przyrost_naturalny_na_1000': 1.2, 'saldo_migracji': -557},
        {'lata': 2010, 'ludnosc_ogolem': 124691, 'urodzenia_zywe': 1286, 'zgony_ogolem': 1182, 'przyrost_naturalny_na_1000': 0.8, 'saldo_migracji': -585},
        {'lata': 2015, 'ludnosc_ogolem': 121731, 'urodzenia_zywe': 1101, 'zgony_ogolem': 1209, 'przyrost_naturalny_na_1000': -0.9, 'saldo_migracji': -503},
        {'lata': 2020, 'ludnosc_ogolem': 114974, 'urodzenia_zywe': 966, 'zgony_ogolem': 1667, 'przyrost_naturalny_na_1000': -6.1, 'saldo_migracji': -295},
        {'lata': 2023, 'ludnosc_ogolem': 111190, 'urodzenia_zywe': 654, 'zgony_ogolem': 1394, 'przyrost_naturalny_na_1000': -6.6, 'saldo_migracji': -471},
    ]

# --- DANE DLA BUDŻETU (NOWE) ---
def get_data_budzet_simulation():
    """Symuluje pobranie danych budżetowych z bazy SQL dla wykresów kołowych."""
    return {
        'year': 2024,
        'dochody': {
            'naglowek': 'Struktura Dochodów Miasta 2024',
            'opis': 'Największe dochody Płocka pochodzą z udziału w podatku PIT (40.5%) oraz dotacji celowych (25.1%).',
            'kategorie': [
                {'nazwa': 'Udział w podatkach PIT/CIT', 'wartosc': 40.5, 'kolor': '#007aff'},
                {'nazwa': 'Dotacje celowe i subwencje', 'wartosc': 25.1, 'kolor': '#34c759'},
                {'nazwa': 'Podatki i opłaty lokalne', 'wartosc': 18.0, 'kolor': '#ff9500'},
                {'nazwa': 'Majątek i Inwestycje', 'wartosc': 9.4, 'kolor': '#5856d6'},
                {'nazwa': 'Inne', 'wartosc': 7.0, 'kolor': '#aeaeb3'}
            ]
        },
        'wydatki': {
            'naglowek': 'Struktura Wydatków Miasta 2024',
            'opis': 'Najwięcej środków budżetowych pochłaniają Oświata i Wychowanie (35.1%) oraz Transport i Drogi (28.9%), co jest typowe dla dużych miast.',
            'kategorie': [
                {'nazwa': 'Oświata i Wychowanie', 'wartosc': 35.1, 'kolor': '#ff3b30'},
                {'nazwa': 'Transport i Drogi', 'wartosc': 28.9, 'kolor': '#007aff'},
                {'nazwa': 'Pomoc Społeczna i Rodzina', 'wartosc': 15.5, 'kolor': '#ffcc00'},
                {'nazwa': 'Gospodarka Komunalna/Ochrona Środ.', 'wartosc': 10.0, 'kolor': '#34c759'},
                {'nazwa': 'Administracja i Bezpieczeństwo', 'wartosc': 6.5, 'kolor': '#5856d6'},
                {'nazwa': 'Kultura i Sport', 'wartosc': 4.0, 'kolor': '#aeaeb3'}
            ]
        },
        'podsumowanie': {
            'wartosc_budzetu': '1 250 000 000 PLN',
            'deficyt': '20 000 000 PLN',
            'komentarz_ai': 'Deficyt budżetowy na poziomie 1.6% planowanych wydatków jest stabilny i świadczy o zrównoważonym zarządzaniu finansami publicznymi Płocka.'
        }
    }


# --- DANE DLA ŚRODOWISKA ---
def get_data_srodowisko_simulation():
    """Symuluje pobranie danych środowiskowych."""
    return [
        {'miesiac': 'Sty', 'pm10_avg': 65, 'energia_kwh': 120000, 'hałas': 68},
        {'miesiac': 'Lut', 'pm10_avg': 78, 'energia_kwh': 115000, 'hałas': 69},
        {'miesiac': 'Mar', 'pm10_avg': 45, 'energia_kwh': 95000, 'hałas': 66},
        {'miesiac': 'Kwi', 'pm10_avg': 30, 'energia_kwh': 85000, 'hałas': 62},
        {'miesiac': 'Maj', 'pm10_avg': 20, 'energia_kwh': 80000, 'hałas': 60},
        {'miesiac': 'Cze', 'pm10_avg': 18, 'energia_kwh': 75000, 'hałas': 61},
    ]

# --- DANE DLA TRANSPORTU ---
def get_data_transport_simulation():
    """Symuluje pobranie danych dotyczących mobilności."""
    return [
        {'miesiac': 'Sty', 'ruch_glowny': 15000, 'km_pasazerowie': 80000, 'wypadki': 12},
        {'miesiac': 'Lut', 'ruch_glowny': 16500, 'km_pasazerowie': 75000, 'wypadki': 15},
        {'miesiac': 'Mar', 'ruch_glowny': 18000, 'km_pasazerowie': 90000, 'wypadki': 8},
        {'miesiac': 'Kwi', 'ruch_glowny': 19500, 'km_pasazerowie': 95000, 'wypadki': 10},
        {'miesiac': 'Maj', 'ruch_glowny': 21000, 'km_pasazerowie': 105000, 'wypadki': 7},
        {'miesiac': 'Cze', 'ruch_glowny': 22000, 'km_pasazerowie': 110000, 'wypadki': 5},
    ]


# ==============================================================================
# 2. LOGIKA PRZETWARZANIA DANYCH I ANALIZA AI
# ==============================================================================

def calculate_summary_demografia(data):
    """Generuje kluczowe statystyki dla bloku AI (strona główna)."""
    if not data:
        return {'lata_zakresu': 'N/A', 'ludnosc_aktualna': 'N/A', 'przyrost_naturalny_na_1000': 'N/A', 'najnowszy_rok': 'N/A', 'saldo_migracji': 'N/A', 'komentarz_ai': 'Brak danych do analizy.'}
        
    latest_data = data[-1]
    max_population_year = max(data, key=lambda x: x['ludnosc_ogolem'])
    
    komentarz_ai = (
        f"Analiza danych za {latest_data['lata']} rok sygnalizuje kluczowe, strategiczne wyzwanie dla Płocka: trwały, ujemny trend demograficzny. "
        f"Wskaźniki takie jak ujemny przyrost naturalny i saldo migracji wprost wskazują na konieczność natychmiastowej, data-driven interwencji. "
        f"Ten Dashboard zapewnia pełną transparentność i jest narzędziem, aby wspólnie z mieszkańcami monitorować skuteczność nowych polityk – w tym inwestycji w mieszkalnictwo i programów wsparcia – które mają za zadanie odwrócić ten trend i budować stabilną przyszłość miasta."
    )
    
    summary = {
        'lata_zakresu': f"{data[0]['lata']} - {latest_data['lata']}",
        'ludnosc_aktualna': f"{latest_data['ludnosc_ogolem']:,}".replace(',', ' '), 
        'przyrost_naturalny_na_1000': f"{latest_data['przyrost_naturalny_na_1000']}".replace('.', ','),
        'najnowszy_rok': latest_data['lata'],
        'saldo_migracji': f"{latest_data['saldo_migracji']:,}".replace(',', ' '),
        'max_ludnosc_z_rokiem': f"{max_population_year['ludnosc_ogolem']:,}".replace(',', ' ') + f" ({max_population_year['lata']})",
        'komentarz_ai': komentarz_ai
    }
    return summary


def calculate_summary_srodowisko(data):
    """Generuje kluczowe statystyki dla bloku AI (Środowisko)."""
    if not data:
        return {'pm10_aktualne': 'N/A', 'halas_srednia': 'N/A', 'zuzycie_wody_zmiana': 'N/A', 'segregacja_procent': 'N/A', 'komentarz_ai': 'Brak danych do analizy środowiskowej.', 'najnowszy_rok': '2025'}
    
    latest_data = data[-1]
    
    komentarz_ai = (
        f"Analiza danych IoT i stacji GIOŚ potwierdza bardzo dobrą jakość powietrza w miesiącach letnich (PM10: {latest_data['pm10_avg']} µg/m³). "
        f"Kluczowym wyzwaniem pozostaje optymalizacja zużycia zasobów miejskich, gdzie mały spadek zużycia wody wskazuje na pozytywny trend dbałości o środowisko. "
        f"Kontynuacja inwestycji w efektywność energetyczną jest niezbędna, aby utrzymać ten pozytywny trend przez cały rok."
    )

    summary = {
        'pm10_aktualne': latest_data['pm10_avg'],
        'halas_srednia': latest_data['hałas'],
        'zuzycie_wody_zmiana': round(random.uniform(-3.0, 1.0), 1),
        'segregacja_procent': 65,
        'komentarz_ai': komentarz_ai,
        'najnowszy_rok': 'Czerwiec'
    }
    return summary


def calculate_summary_transport(data):
    """Generuje kluczowe statystyki dla bloku AI (Transport)."""
    if not data:
        return {'punktualnosc_km': 'N/A', 'wypadki_miesiac': 'N/A', 'srednia_predkosc': 'N/A', 'sciezki_km': 'N/A', 'komentarz_ai': 'Brak danych transportowych.', 'najnowszy_rok': '2025'}
    
    latest_data = data[-1]

    komentarz_ai = (
        f"Analiza danych za {latest_data['miesiac']} pokazuje, że ruch drogowy osiągnął szczyt, co wymaga natychmiastowej optymalizacji sygnalizacji świetlnej i koordynacji remontów. "
        f"Jednocześnie, liczba pasażerów KM wzrasta, potwierdzając skuteczność inwestycji w komunikację publiczną. "
        f"Priorytetem musi być teraz poprawa bezpieczeństwa i płynności ruchu."
    )

    summary = {
        'punktualnosc_km': 98.2,
        'wypadki_miesiac': latest_data['wypadki'],
        'srednia_predkosc': 32,
        'sciezki_km': 78, # Stała wartość dla demo
        'komentarz_ai': komentarz_ai,
        'najnowszy_rok': latest_data['miesiac']
    }
    return summary


def prepare_chart_data(data, label_key, value_key):
    """Przygotowuje dane do Chart.js w formacie JSON dla wykresów liniowych/słupkowych."""
    labels = [row[label_key] for row in data]
    values = [row[value_key] for row in data]
    return json.dumps({'labels': labels, 'data': values}) 

def prepare_budget_chart_data(budget_data):
    """Przetwarza dane budżetowe do JSON dla Chart.js (wykresy kołowe)."""
    chart_data = {}
    for key in ['dochody', 'wydatki']:
        d = budget_data[key]
        labels = [k['nazwa'] for k in d['kategorie']]
        data = [k['wartosc'] for k in d['kategorie']]
        colors = [k['kolor'] for k in d['kategorie']]
        
        chart_data[key] = json.dumps({
            'labels': labels, 
            'data': data, 
            'colors': colors,
            'opis': d['opis']
        })
    return chart_data


# ==============================================================================
# 3. FUNKCJE WIDOKU (ROUTES)
# ==============================================================================

@app.route('/')
def index():
    # --- DEMOGRAFIA ---
    raw_data = get_data_demografia_simulation()
    summary = calculate_summary_demografia(raw_data) 
    chart_data_json = prepare_chart_data(raw_data, 'lata', 'przyrost_naturalny_na_1000')
    
    # Tabela: Mapowanie kluczy SQL na nazwy wyświetlane w tabeli
    display_headers = ['Lata', 'Ludność ogółem', 'Urodzenia żywe', 'Zgony ogółem', 'Przyrost naturalny (‰)', 'Saldo migracji']
    display_data = []
    
    for row in raw_data:
        display_data.append({
            'Lata': row['lata'],
            'Ludność ogółem': f"{row['ludnosc_ogolem']:,}".replace(',', ' '),
            'Urodzenia żywe': f"{row['urodzenia_zywe']:,}".replace(',', ' '),
            'Zgony ogółem': f"{row['zgony_ogolem']:,}".replace(',', ' '),
            'Przyrost naturalny (‰)': f"{row['przyrost_naturalny_na_1000']}".replace('.', ','),
            'Saldo migracji': f"{row['saldo_migracji']:,}".replace(',', ' '),
        })

    # Dokumentacja
    documentation_files = [
        {"name": "OBJAŚNIENIA ZNAKÓW.doc", "desc": "Międzynarodowe znaki umowne i skróty statystyczne GUS."},
        {"name": "1.7. Miasta partnerskie(2).doc", "desc": "Lista miast partnerskich Płocka i historia współpracy."},
        {"name": "Api i bdl", "desc": "Linki do API GUS i Banku Danych Lokalnych."},
        {"name": "1.1. Ludność w osiedlach.ods", "desc": "Dodatkowe dane o ludności z podziałem na osiedla (gotowe do importu)."},
    ]

    return render_template('index.html', 
                           display_headers=display_headers, 
                           display_data=display_data, 
                           summary=summary,
                           chart_data=chart_data_json,
                           documentation_files=documentation_files)


@app.route('/budzet')
def budzet():
    # --- BUDŻET (NOWA TRASA) ---
    budget_data_raw = get_data_budzet_simulation()
    chart_data = prepare_budget_chart_data(budget_data_raw)
    
    # Dokumentacja budżetowa
    documentation_files = [
        {"name": "Uchwała Budżetowa 2024", "desc": "Oficjalna uchwała budżetowa Rady Miasta Płocka."},
        {"name": "Plan Wydatków Inwestycyjnych", "desc": "Szczegółowa lista projektów infrastrukturalnych."},
        {"name": "OBJAŚNIENIA ZNAKÓW.doc", "desc": "Używane skróty i oznaczenia statystyczne."},
    ]
    
    return render_template('budzet.html', 
                           budget_data=budget_data_raw,
                           chart_data_dochody=chart_data['dochody'],
                           chart_data_wydatki=chart_data['wydatki'],
                           documentation_files=documentation_files) # Dodajemy dokumentację!


@app.route('/srodowisko')
def enviroment(): 
    # --- ŚRODOWISKO ---
    raw_data = get_data_srodowisko_simulation() 
    summary = calculate_summary_srodowisko(raw_data) 
    
    # Wykresy
    chart_data_1 = prepare_chart_data(raw_data, 'miesiac', 'pm10_avg')
    chart_data_2 = prepare_chart_data(raw_data, 'miesiac', 'energia_kwh')
    
    # Tabela szczegółowa
    display_data = [
        {'Miesiąc': d['miesiac'], 'Średnie PM10 (µg/m³)': d['pm10_avg'], 'Zużycie Energii (kWh)': f"{d['energia_kwh']:,}".replace(',', ' '), 'Śr. Hałas (dB)': d['hałas']} for d in raw_data
    ]
    display_headers = list(display_data[0].keys())

    # Dokumentacja
    documentation_files = [
        {"name": "Raport PM10", "desc": "Roczny raport z GIOŚ i stacji miejskich."},
        {"name": "EKO-Inwestycje 2024", "desc": "Lista projektów termomodernizacyjnych i paneli PV."},
        {"name": "OBJAŚNIENIA ZNAKÓW.doc", "desc": "Używane skróty i oznaczenia statystyczne."},
    ]

    return render_template('srodowisko.html',
                           summary=summary,
                           chart_data_1=chart_data_1,
                           chart_data_2=chart_data_2,
                           display_data=display_data,
                           display_headers=display_headers,
                           documentation_files=documentation_files
                           )

@app.route('/transport')
def transport():
    # --- TRANSPORT ---
    raw_data = get_data_transport_simulation() 
    summary = calculate_summary_transport(raw_data) 
    
    # Wykresy
    chart_data_1 = prepare_chart_data(raw_data, 'miesiac', 'ruch_glowny')
    chart_data_2 = prepare_chart_data(raw_data, 'miesiac', 'km_pasazerowie')
    
    # Tabela szczegółowa
    display_data = [
        {'Miesiąc': d['miesiac'], 'Ruch Główny': f"{d['ruch_glowny']:,}".replace(',', ' '), 'Pasażerowie KM': f"{d['km_pasazerowie']:,}".replace(',', ' '), 'Wypadki/Miesiąc': d['wypadki']} for d in raw_data
    ]
    display_headers = list(display_data[0].keys())

    # Dokumentacja
    documentation_files = [
        {"name": "Raport Wypadków 2024", "desc": "Statystyki Policji i PSP dot. zdarzeń drogowych."},
        {"name": "Plan Mobilności Płock 2030", "desc": "Strategia rozwoju transportu publicznego i rowerowego."},
        {"name": "OBJAŚNIENIA ZNAKÓW.doc", "desc": "Używane skróty i oznaczenia statystyczne."},
    ]

    return render_template('transport.html',
                           summary=summary,
                           chart_data_1=chart_data_1,
                           chart_data_2=chart_data_2,
                           display_data=display_data,
                           display_headers=display_headers,
                           documentation_files=documentation_files
                           )


@app.route('/export')
def export_data():
    """Endpoint do eksportu danych z SQL do CSV. Eksportuje dane demograficzne (główne)."""
    data = get_data_demografia_simulation()
    
    si = StringIO()
    fieldnames = list(data[0].keys()) if data else []
    
    writer = csv.DictWriter(si, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    writer.writerows(data)
    
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = "attachment; filename=urbandata_plock_statystyki_SQL.csv"
    return output




if __name__ == '__main__':
    
    app.run(debug=True, port=8000)