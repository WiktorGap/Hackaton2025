# app.py
from flask import Flask, render_template, Response
import json
import csv
from io import StringIO

app = Flask(__name__)

# ==============================================================================
# BAZA DANYCH (MOCK SQL) - TUTAJ PODŁĄCZYSZ SWÓJ SQL!
# ==============================================================================
def get_data_from_sql_simulation():
    """ 
    Ta funkcja symuluje wynik zapytania SELECT * FROM plock_statystyki;
    W Twoim finalnym projekcie, w tym miejscu wstawisz kod do połączenia
    z bazą danych (np. za pomocą SQLAlchemy lub psycopg2).
    """
    # Dane są już czyste, znormalizowane i gotowe do użycia
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

# ==============================================================================
# LOGIKA DASHBOARDU I ANALIZA AI (BLOCKQUOTE)
# ==============================================================================
def calculate_summary(data):
    """Generuje kluczowe statystyki dla bloku AI (blockquote)."""
    if not data:
        return {'lata_zakresu': 'N/A', 'ludnosc_aktualna': 'N/A', 'przyrost_naturalny_na_1000': 'N/A', 'najnowszy_rok': 'N/A', 'saldo_migracji': 'N/A', 'komentarz_ai': 'Brak danych do analizy.'}
        
    latest_data = data[-1]
    
    # Znajdowanie maksymalnej populacji
    max_population_year = max(data, key=lambda x: x['ludnosc_ogolem'])
    
    # Wstępnie generowany komentarz AI (zwykle pobierany z SQL po przetworzeniu w Make.com/zewn. usłudze)
    komentarz_ai = (
        f"W roku {latest_data['lata']} Płock kontynuuje trend spadkowy w zakresie demografii, odnotowując ujemny przyrost naturalny i ujemne saldo migracji. "
        f"To sygnał dla władz miasta, aby skoncentrować inwestycje na programach wspierających młode rodziny i zatrzymujących odpływ mieszkańców."
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

def prepare_chart_data(data, metric_key):
    """Przygotowuje dane do Chart.js w formacie JSON."""
    years = [row['lata'] for row in data]
    values = [row[metric_key] for row in data]
    return json.dumps({'labels': years, 'data': values}) 

@app.route('/')
def index():
    # 1. POBRANIE DANYCH Z SQL (Symulacja)
    raw_data = get_data_from_sql_simulation()
    
    # 2. LOGIKA I ANALIZA
    summary = calculate_summary(raw_data) 
    
    # 3. WIZUALIZACJA: Dane dla wykresu Przyrostu Naturalnego
    chart_data_json = prepare_chart_data(raw_data, 'przyrost_naturalny_na_1000')
    
    # 4. TABELA: Mapowanie kluczy SQL na nazwy wyświetlane w tabeli
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

    # Przekazujemy listę plików do sekcji Dokumentacja
    documentation_files = [
        {"name": "OBJAŚNIENIA ZNAKÓW.doc", "desc": "Międzynarodowe znaki umowne i skróty statystyczne GUS."},
        {"name": "1.7. Miasta partnerskie(2).doc", "desc": "Lista miast partnerskich Płocka i historia współpracy."},
        {"name": "Api i bdl", "desc": "Linki do API GUS i Banku Danych Lokalnych."},
        {"name": "1.1. Ludność w osiedlach.ods", "desc": "Dodatkowe dane o ludności z podziałem na osiedla (gotowe do importu)."},
    ]


    return render_template('index.html', 
                           display_headers=display_headers, 
                           data=display_data,
                           summary=summary,
                           chart_data=chart_data_json,
                           documentation_files=documentation_files)

@app.route('/export')
def export_data():
    """Endpoint do eksportu danych z SQL do CSV."""
    data = get_data_from_sql_simulation()
    
    si = StringIO()
    fieldnames = list(data[0].keys()) if data else []
    
    # Używamy średnika jako separatora dla kompatybilności z polskimi ustawieniami Excela
    writer = csv.DictWriter(si, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    writer.writerows(data)
    
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = "attachment; filename=urbandata_plock_statystyki_SQL.csv"
    return output

if __name__ == '__main__':
    # Uruchom na porcie 8000, aby mieć pewność, że działa
    app.run(debug=True, port=8000)