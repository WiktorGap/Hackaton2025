from . import main
from datetime import datetime, timezone
from flask import render_template , Response
import pyodbc
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random 
from io import StringIO
import json
import csv
from matplotlib.ticker import MaxNLocator

connection_string_ = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=THINKBOOK_CODE;'
    r'DATABASE=Hackaton;'
    r'Trusted_Connection=yes;'
)


connection_string_1 = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=THINKBOOK_CODE;'
    r'DATABASE=wykroczeniadrogowe;'
    r'Trusted_Connection=yes;'
)



connection_string_2 = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=THINKBOOK_CODE;'
    r'DATABASE=WypadkiDrogowe;'
    r'Trusted_Connection=yes;'
)

# KONFIGURACJA WYKRESÓW DLA KONKRETNYCH TABEL
CHART_CONFIGS = {
    '2.1. Powierzchnia i ludność średnik': {
        'time_series': [
            {
                'x_column': 'Lata',
                'y_column': 'Ludnosc_ogolem', 
                'title': 'Ludność na przestrzeni lat',
                'color': 'blue',
                'line_style': '-'
            },
            {
                'x_column': 'Lata',
                'y_column': 'Kobiety_na_100_mezczyzn',
                'title': 'Liczba kobiet na 100 mężczyzn na przestrzeni lat',
                'color': 'red', 
                'line_style': '-'
            },
            {
                'x_column': 'Lata',
                'y_column': 'Ludnosc_na_1_km_kw',
                'title': 'Zagęszczenie ludności na 1km² na przestrzeni lat',
                'color': 'green',
                'line_style': '-'
            },
            {
                'x_column': 'Lata', 
                'y_column': 'Obszar_km_kw',
                'title': 'Obszar miasta na przestrzeni lat',
                'color': 'purple',
                'line_style': '-'
            }
        ],
        'multi_line': [
            {
                'x_column': 'Lata',
                'y_columns': ['mezczyzni_udzial_w', 'kobiety_udzial_w'],
                'colors': ['blue', 'red'],
                'labels': ['Mężczyźni', 'Kobiety'],
                'title': 'Stosunek procentowy kobiet i mężczyzn w społeczeństwie Płocka na przestrzeni lat'
            }
        ]
    },
    '2.5. Pojedyncze roczniki średnik': {
        'multi_line': [
            {
                'x_column': 'Wiek',
                'y_columns': ['kobiety', 'mezczyzni'],
                'colors': ['red', 'blue'],
                'labels': ['Kobiety', 'Mężczyźni'],
                'title': 'Wiek populacji w społeczeństwie w podziale na płeć',
                'x_ticks_step': 5,  # Pokazuj co 5 rok
                'width_scale': 1.5  # Szerokość wykresu
            }
        ]
    }
}


@main.route('/demography', methods=['GET'])
def displayData():
    try:
        con = pyodbc.connect(connection_string_)
        print("Connection established successfully.")
        
        cursor = con.cursor()
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        charts_data = []
        
        for table_name in tables:
            print(f"Processing table: {table_name}")
            
            df = pd.read_sql(f"SELECT * FROM [{table_name}]", con)
            
            if len(df) > 0:
                table_charts = generate_charts_for_table(df, table_name)
                charts_data.extend(table_charts)
        
        cursor.close()
        con.close()
        
        return render_template('data_display.html', charts_data=charts_data)
        
    except Exception as e:
        print(f"Connection error: {e}")
        return render_template('data_display.html', charts_data=[], error=str(e))

def generate_charts_for_table(df, table_name):
    """Generuje wykresy dla danej tabeli według predefiniowanych reguł"""
    charts = []
    
    # Sprawdź czy istnieje konfiguracja dla tej tabeli
    if table_name in CHART_CONFIGS:
        config = CHART_CONFIGS[table_name]
        charts.extend(generate_configured_charts(df, table_name, config))
    else:
        # Domyślne generowanie wykresów jeśli nie ma konfiguracji
        charts.extend(generate_default_charts(df, table_name))
    
    return charts

def generate_configured_charts(df, table_name, config):
    """Generuje wykresy według specyficznej konfiguracji tabeli"""
    charts = []
    
    # Pojedyncze wykresy liniowe (time series)
    if 'time_series' in config:
        for chart_config in config['time_series']:
            x_col = chart_config['x_column']
            y_col = chart_config['y_column']
            title = chart_config['title']
            color = chart_config.get('color', 'blue')
            line_style = chart_config.get('line_style', '-')
            
            if x_col in df.columns and y_col in df.columns:
                chart = create_line_chart(df, x_col, y_col, table_name, title, color, line_style)
                if chart:
                    charts.append(chart)
    
    # Wykresy z wieloma liniami na jednym wykresie
    if 'multi_line' in config:
        for multi_config in config['multi_line']:
            x_col = multi_config['x_column']
            y_cols = multi_config['y_columns']
            title = multi_config['title']
            colors = multi_config.get('colors', ['blue', 'red', 'green', 'orange'])
            labels = multi_config.get('labels', y_cols)
            x_ticks_step = multi_config.get('x_ticks_step')
            width_scale = multi_config.get('width_scale', 1.0)
            
            if x_col in df.columns and all(y_col in df.columns for y_col in y_cols):
                chart = create_multi_line_chart(df, x_col, y_cols, table_name, title, colors, labels, x_ticks_step, width_scale)
                if chart:
                    charts.append(chart)
    
    return charts

def generate_default_charts(df, table_name):
    """Domyślne generowanie wykresów gdy nie ma specyficznej konfiguracji"""
    charts = []
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    # Jeśli mamy kolumnę 'Lata' i kolumny numeryczne
    if 'Lata' in df.columns and len(numeric_columns) > 0:
        for col in numeric_columns:
            if col != 'Lata':
                chart = create_line_chart(df, 'Lata', col, table_name, f'{col} w czasie')
                if chart:
                    charts.append(chart)
    
    return charts

def create_line_chart(df, x_col, y_col, table_name, title, color='blue', line_style='-'):
    """Tworzy wykres liniowy"""
    try:
        plt.figure(figsize=(12, 7))
        plt.plot(df[x_col], df[y_col], marker='o', linewidth=2.5, 
                markersize=6, color=color, linestyle=line_style)
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(x_col, fontsize=12)
        plt.ylabel(y_col, fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return save_chart_to_base64(table_name, title)
    except Exception as e:
        print(f"Error creating line chart for {y_col}: {e}")
        plt.close()
        return None

def create_multi_line_chart(df, x_col, y_cols, table_name, title, colors, labels, x_ticks_step=None, width_scale=1.0):
    """Tworzy wykres z wieloma liniami"""
    try:
       
        base_width = 12
        calculated_width = max(base_width, len(df) * 0.15) * width_scale
        plt.figure(figsize=(calculated_width, 7))
        
        for i, y_col in enumerate(y_cols):
            color = colors[i % len(colors)]
            label = labels[i % len(labels)]
            plt.plot(df[x_col], df[y_col], marker='o', linewidth=2, 
                    markersize=4, color=color, label=label, alpha=0.8)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(x_col, fontsize=12)
        plt.ylabel('Liczba ludności', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best')
      
        if x_ticks_step is not None and len(df) > x_ticks_step:
            # Pokazuj tylko co x-tą etykietę
            ticks = df[x_col][::x_ticks_step]
            plt.xticks(ticks, rotation=45, fontsize=10)
        else:
            # Dla mniejszej liczby punktów pokazuj wszystkie etykiety
            plt.xticks(rotation=45, fontsize=10)
        
        # Zwiększ odstępy między subplotami aby zmieścić etykiety
        plt.tight_layout(pad=3.0)
        
        return save_chart_to_base64(table_name, title)
    except Exception as e:
        print(f"Error creating multi-line chart: {e}")
        plt.close()
        return None

def save_chart_to_base64(table_name, chart_name):
    """Zapisuje aktualny wykres do base64 i zamyka figure"""
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    
    return {
        'table_name': table_name,
        'chart_name': chart_name,
        'chart_data': chart_base64
    }







def get_budget_comparative_data():
    """Pobiera dane z tabeli Budzet (porównanie miast) z bazy danych"""
    try:
        conn = pyodbc.connect(connection_string_)
        query = "SELECT * FROM [Hackaton].[dbo].[Budzet]"
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Konwersja kolumn numerycznych, ignorowanie błędów
        numeric_cols = ['Zplanowana kwota', 'na mieszkańca', 'Zgłoszone projekty', 'Głosujący na projekty']
        for col in numeric_cols:
            if col in df.columns:
                # Zamiana przecinka na kropkę i konwersja na float
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce') 
        
        return df
    except Exception as e:
        print(f"Błąd podczas pobierania danych Budzet (porównawcze): {e}")
        return None
    

    # W pliku routes.py

# ... (po funkcjach create_posiedzenia_charts lub w sekcji tworzenia wykresów)

def create_comparative_budget_chart(df, y_col='na mieszkańca', title_suffix=' Budżet na Mieszkańca'):
    """Tworzy wykres słupkowy porównujący miasta, z Płockiem zaznaczonym na czerwono."""
    
    if df is None or df.empty or 'Miasto' not in df.columns or y_col not in df.columns:
        return None
    
    df_sorted = df.sort_values(by=y_col, ascending=False).reset_index(drop=True)
    
    # Określenie kolorów: czerwony dla Płocka, niebieski dla reszty
    colors = ['red' if miasto == 'Płock' else 'darkblue' for miasto in df_sorted['Miasto']]
    
    try:
        plt.figure(figsize=(14, 7))
        bars = plt.bar(df_sorted['Miasto'], df_sorted[y_col], color=colors, alpha=0.8)
        
        plt.title(f'Porównanie Budżetu Obywatelskiego - {title_suffix}', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Miasto', fontsize=12)
        plt.ylabel(f'{y_col} (zł)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        
        # Dodanie wartości na słupkach
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Zapis do base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close()
        
        return {
            'title': f'Budżet Obywatelski na mieszkańca (Porównanie Miast)',
            'description': f'Porównanie budżetu obywatelskiego przeznaczonego na jednego mieszkańca w różnych miastach. Wyróżniono **Płock** kolorem czerwonym.',
            'chart_data': chart_base64
        }
    except Exception as e:
        print(f"Błąd tworzenia wykresu porównawczego: {e}")
        plt.close()
        return None
    


@main.route('/budget_comparative', methods=['GET'])
def display_budget_comparative():
    """Wyświetla wykres porównawczy budżetu obywatelskiego dla miast."""
    df = get_budget_comparative_data()
    
    if df is None or df.empty:
        return render_template('data_display.html', 
                             error="Nie udało się pobrać danych porównawczych budżetu miast",
                             charts=[])

    # Generowanie wykresu porównawczego na podstawie kolumny 'na mieszkańca'
    charts = [create_comparative_budget_chart(df, y_col='na mieszkańca', title_suffix='Budżet na Mieszkańca')]
    
    # Możesz dodać więcej wykresów, np. porównanie zgłoszonych projektów
    charts.append(create_comparative_budget_chart(df, y_col='Zgłoszone projekty', title_suffix='Liczba Zgłoszonych Projektów'))
    
    # Filtruj None'y
    charts = [chart for chart in charts if chart is not None]

    # Obliczenie ogólnych statystyk dla sekcji statystyk (na potrzeby szablonu)
    stats = {
        'total_cities': len(df),
        'total_budget': f"{(df['Zplanowana kwota'].sum() / 1_000_000):.2f}" if 'Zplanowana kwota' in df.columns else "N/A",
        'avg_budget_per_capita': f"{df['na mieszkańca'].mean():.2f}" if 'na mieszkańca' in df.columns else "N/A",
        'total_voters': f"{df['Głosujący na projekty'].sum():,}".replace(',', ' ') if 'Głosujący na projekty' in df.columns else "N/A"
    }
    
    return render_template('chart_dashboard.html', 
                           charts=charts, 
                           stats=stats, 
                           error=None,
                           page_title="Porównanie Budżetów Obywatelskich Miast")




CHART_CONFIGS = {
    '2.1. Powierzchnia i ludność średnik': {
        'time_series': [
            {
                'x_column': 'Lata',
                'y_column': 'Ludnosc_ogolem', 
                'title': 'Ludność na przestrzeni lat',
                'color': 'blue',
                'line_style': '-'
            },
            {
                'x_column': 'Lata',
                'y_column': 'Kobiety_na_100_mezczyzn',
                'title': 'Liczba kobiet na 100 mężczyzn na przestrzeni lat',
                'color': 'red', 
                'line_style': '-'
            },
            {
                'x_column': 'Lata',
                'y_column': 'Ludnosc_na_1_km_kw',
                'title': 'Zagęszczenie ludności na 1km² na przestrzeni lat',
                'color': 'green',
                'line_style': '-'
            },
            {
                'x_column': 'Lata', 
                'y_column': 'Obszar_km_kw',
                'title': 'Obszar miasta na przestrzeni lat',
                'color': 'purple',
                'line_style': '-'
            }
        ],
        'multi_line': [
            {
                'x_column': 'Lata',
                'y_columns': ['mezczyzni_udzial_w', 'kobiety_udzial_w'],
                'colors': ['blue', 'red'],
                'labels': ['Mężczyźni', 'Kobiety'],
                'title': 'Stosunek procentowy kobiet i mężczyzn w społeczeństwie Płocka na przestrzeni lat'
            }
        ]
    },
    '2.5. Pojedyncze roczniki średnik': {
        'multi_line': [
            {
                'x_column': 'Wiek',
                'y_columns': ['kobiety', 'mezczyzni'],
                'colors': ['red', 'blue'],
                'labels': ['Kobiety', 'Mężczyźni'],
                'title': 'Wiek populacji w społeczeństwie w podziale na płeć',
                'x_ticks_step': 5,  # Pokazuj co 5 rok
                'width_scale': 1.5  # Szerokość wykresu
            }
        ]
    },
    # --- NOWA KONFIGURACJA DLA BUDŻETU OBYWATELSKIEGO PŁOCKA ---
    # ZASTĄP SEKCJE 'BudzetObywatelskiPlock_Wykresy' w Twoim słowniku CHART_CONFIGS tym poniżej:
'BudzetObywatelskiPlock_Wykresy': {
    'time_series_multi': [ 
        {
            # Wykres 1: Frekwencja (Pozostaje słupkowy, ale z korektą tytułu i opisu)
            'x_column': 'Rok głosowania',
            'y_columns': [
                'Frekwencja w %',
            ],
            'colors': ['#e74c3c'], 
            'labels': ['Frekwencja'],
            'title': 'Frekwencja w głosowaniach na Budżet Obywatelski w Płocku',
            'ylabel': 'Frekwencja w %',
            'description': 'Zmiana frekwencji w Budżecie Obywatelskim na przestrzeni lat.',
            'chart_type': 'bar_single' # Zmieniono z 'line_with_bar' na 'bar_single'
        },
        {
            # Wykres 2: Udział mieszkańców (Zmieniony na słupkowy - bar_multi)
            'x_column': 'Rok głosowania',
            'y_columns': [
                'Liczba uprawnionych do głosowania',
                'Liczba głosujących ogółem'
            ],
            'colors': ['#3498db', '#2ecc71'], 
            'labels': ['Uprawnieni', 'Głosujący'],
            'title': 'Udział mieszkańców w głosowaniu na BO',
            'ylabel': 'Liczba osób',
            'description': 'Porównanie liczby uprawnionych do głosowania z faktyczną liczbą głosujących ogółem (wykres słupkowy).',
            'chart_type': 'bar_multi' # Zmieniono z 'multi_line' na 'bar_multi'
        },
        {
            # Wykres 3: Kwota BO (Zmieniony tytuł, typ na bar_single)
            'x_column': 'Rok głosowania',
            'y_columns': [
                'Kwota przeznaczona na realizację BO w zł'
            ],
            'colors': ['#f39c12'], 
            'labels': ['Kwota BO'],
            'title': 'Kwoty przeznaczone na budżet obywatelski', # ZMIANA TYTUŁU
            'ylabel': 'Kwota w zł',
            'description': 'Trend kwoty przeznaczonej na realizację Budżetu Obywatelskiego w kolejnych latach (wykres słupkowy).',
            'chart_type': 'bar_single' # Zmieniono z 'bar' na 'bar_single'
        },
        {
            # Wykres 4: Proces weryfikacji projektów (Zmieniony na słupkowy grupowany - bar_multi)
            'x_column': 'Rok głosowania',
            'y_columns': [
                'Liczba projektów złożonych ogółem',
                'Liczba projektów pozytywnie zweryfikowanych ogółem',
                'Liczba projektów wybranych do realizacji ogółem'
            ],
            'colors': ['#9b59b6', '#34495e', '#1abc9c'], 
            'labels': ['Złożone', 'Zweryfikowane', 'Wybrane do Realizacji'],
            'title': 'Proces weryfikacji projektów BO',
            'ylabel': 'Liczba projektów',
            'description': 'Liczba projektów złożonych, pozytywnie zweryfikowanych i ostatecznie wybranych do realizacji (wykres słupkowy grupowany).',
            'chart_type': 'bar_multi' # Zmieniono z 'multi_line' na 'bar_multi'
        }
    ]
},
}




def get_bo_plock_data_for_charts():
    """Pobiera i czyści dane z tabeli BudzetObywatelskiPlock, z unikalną nazwą funkcji."""
    try:
        conn = pyodbc.connect(connection_string_)
        query = "SELECT * FROM [Hackaton].[dbo].[BudzetObywatelskiPlock]"
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Konwersja kolumn numerycznych
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Zamień przecinek na kropkę, usuń spacje i przekonwertuj na float
                    df[col] = df[col].astype(str).str.replace(' ', '', regex=False).str.replace(',', '.', regex=False)
                    df[col] = pd.to_numeric(df[col], errors='coerce') 
                except:
                    pass
            elif col in ['Numer edycji Budżetu Obywatelskiego', 'Rok głosowania']:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        return df
    except Exception as e:
        print(f"Błąd podczas pobierania danych BudzetObywatelskiPlock (get_bo_plock_data_for_charts): {e}")
        return None



def create_bo_plock_time_series_chart(df, x_col, y_cols, table_name, title, colors, labels, ylabel, chart_type, description):
    """Tworzy wykres liniowy, słupkowy lub grupowany słupkowy dla trendów BO Płocka."""
    try:
        df = df.sort_values(by=x_col).dropna(subset=[x_col] + y_cols)
        
        # Ustalenie rozmiaru wykresu
        base_width = 12
        calculated_width = max(base_width, len(df) * 0.8) 
        plt.figure(figsize=(calculated_width, 7))
        
        # Słupki będą miały szerokość 0.8 / (liczba serii)
        N = len(df)
        ind = np.arange(N)
        width = 0.8 / len(y_cols)
        
        # Formater dla dużych liczb (z zerami na końcu)
        def format_y_value(val):
            if val >= 1000:
                return f"{val:,.0f}".replace(",", " ").replace(".0", "")
            return f"{val:.1f}".replace('.', ',')

        
        if chart_type == 'multi_line':
            # WYKRES LINIOWY (zachowany na wypadek, gdyby był potrzebny)
            for i, y_col in enumerate(y_cols):
                color = colors[i % len(colors)]
                label = labels[i % len(labels)]
                plt.plot(df[x_col], df[y_col], marker='o', linewidth=3, 
                         markersize=7, color=color, label=label, alpha=0.8)
            plt.legend(loc='best', fontsize=10)
        
        elif chart_type == 'bar_single':
            # WYKRES SŁUPKOWY POJEDYNCZY (Kwota, Frekwencja)
            y_col = y_cols[0]
            color = colors[0]
            label = labels[0]
            
            bars = plt.bar(df[x_col], df[y_col], color=color, alpha=0.8, label=label, width=0.6)

            # Dodanie wartości na słupkach
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2.0, yval, 
                         format_y_value(yval) + ('%' if 'Frekwencja' in y_col else ''), 
                         ha='center', va='bottom', fontsize=10, rotation=45 if 'Kwota' in y_col else 0)

        elif chart_type == 'bar_multi':
            # WYKRES SŁUPKOWY GRUPOWANY (Udział, Projekty)
            
            # Tworzenie grup słupków obok siebie
            for i, y_col in enumerate(y_cols):
                color = colors[i % len(colors)]
                label = labels[i % len(labels)]
                
                # Przesunięcie słupka w ramach grupy
                current_ind = ind + i * width - (len(y_cols) - 1) * width / 2
                bars = plt.bar(current_ind, df[y_col], width, color=color, alpha=0.8, label=label)

                # Dodanie wartości na słupkach
                for bar in bars:
                    yval = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2.0, yval, 
                             format_y_value(yval), 
                             ha='center', va='bottom', fontsize=8, color='black') # Mniejsza czcionka dla lepszej czytelności w grupach
            
            # Ustawienie etykiet X na środek grup
            plt.xticks(ind, df[x_col].unique(), rotation=45, fontsize=10)
            plt.legend(loc='best', fontsize=10)
            
        else: # Domyślnie - powrót do multi_line jeśli nieznany typ
             for i, y_col in enumerate(y_cols):
                color = colors[i % len(colors)]
                label = labels[i % len(labels)]
                plt.plot(df[x_col], df[y_col], marker='o', linewidth=3, 
                         markersize=7, color=color, label=label, alpha=0.8)
             plt.legend(loc='best', fontsize=10)


        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(x_col, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, axis='y', alpha=0.3)
        
        # Koniec
        plt.tight_layout(pad=3.0)
        
        chart_info = save_chart_to_base64(table_name, title)
        chart_info['description'] = description
        return chart_info

    except Exception as e:
        print(f"Błąd tworzenia wykresu Budżetu Obywatelskiego ({title}): {e}")
        plt.close()
        return None




@main.route('/budzet_obywatelski_plock_dashboard', methods=['GET'])
def display_budget_plock_dashboard():
    """Wyświetla wykresy i statystyki dla tabeli BudzetObywatelskiPlock."""
    
    # 1. Pobieranie danych (nowa funkcja)
    df = get_bo_plock_data_for_charts()
    
    if df is None or df.empty:
        return render_template('chart_dashboard.html', 
                             error="Nie udało się pobrać danych Budżetu Obywatelskiego Płocka (Błąd połączenia lub puste dane).",
                             charts=[],
                             page_title="Budżet Obywatelski Płocka")
    
    # 2. Generowanie wykresów (nowa konfiguracja i funkcja)
    charts = []
    config = CHART_CONFIGS.get('BudzetObywatelskiPlock_Wykresy')
    
    if config and 'time_series_multi' in config:
        for chart_conf in config['time_series_multi']:
            chart = create_bo_plock_time_series_chart(
                df, 
                x_col=chart_conf['x_column'],
                y_cols=chart_conf['y_columns'],
                table_name='BudzetObywatelskiPlock',
                title=chart_conf['title'],
                colors=chart_conf['colors'],
                labels=chart_conf['labels'],
                ylabel=chart_conf['ylabel'],
                chart_type=chart_conf['chart_type'],
                description=chart_conf['description']
            )
            if chart:
                charts.append({
                    'title': chart_conf['title'],
                    'description': chart_conf['description'],
                    'chart_data': chart['chart_data']
                })
                
    # 3. Obliczanie statystyk (dla górnego panelu)
    total_budget = df['Kwota przeznaczona na realizację BO w zł'].sum()
    total_voters = df['Liczba głosujących ogółem'].sum()
    avg_frekwencja = df['Frekwencja w %'].mean()
    min_year = df['Rok głosowania'].min()
    max_year = df['Rok głosowania'].max()
    
    def format_big_number(n):
        return f"{n:,.0f}".replace(",", " ")

    stats = {
        'total_budget_zl': f"{format_big_number(total_budget)} zł",
        'total_voters': format_big_number(total_voters),
        'avg_frekwencja': f"{avg_frekwencja:.2f}%",
        'data_range': f"{min_year} - {max_year}",
    }
    
    # 4. Renderowanie
    return render_template('chart_dashboard.html', 
                         charts=charts, 
                         stats=stats, 
                         error=None,
                         page_title="Budżet Obywatelski Płocka")















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

@main.route('/')
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


@main.route('/budzet')
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


@main.route('/srodowisko')
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

@main.route('/transport')
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


@main.route('/export')
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


def pobierz_dane_z_bazy():
    """Pobiera dane z bazy SQL Server"""
    server = 'localhost'
    database = 'WykroczeniaDrogowe'
    
    conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    try:
        conn = pyodbc.connect(connection_string_1)
        cursor = conn.cursor()
        cursor.execute("SELECT Rok, LiczbaWykroczeniDrogowych FROM WykroczeniaDrogowe ORDER BY Rok")
        dane = cursor.fetchall()
        conn.close()
        return dane
    except Exception as e:
        print(f"Błąd: {e}")
        return None


def utworz_wykres_base64():
    """Tworzy wykres i zwraca jako string Base64"""
    dane = pobierz_dane_z_bazy()
    
    if not dane:
        return None
    
    lata = [row[0] for row in dane]
    liczby = [row[1] for row in dane]
    
    # Stwórz figurę z lepszymi proporcjami
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Utwórz gradient kolorów dla słupków
    colors = plt.cm.viridis([(i / len(lata)) for i in range(len(lata))])
    
    # Stwórz słupki z cieniami i zaokrąglonymi krawędziami
    bars = ax.bar(lata, liczby, color=colors, edgecolor='white', 
                  linewidth=2, width=0.7, alpha=0.9)
    
    # Dodaj cienie dla głębi
    for bar in bars:
        bar.set_zorder(3)
    
    # Formatowanie osi
    ax.set_xlabel('Rok', fontsize=14, fontweight='bold', color='#333333')
    ax.set_ylabel('Liczba wykroczeń drogowych', fontsize=14, fontweight='bold', color='#333333')
    ax.set_title('Wykroczenia drogowe w latach 2020-2023', 
                 fontsize=16, fontweight='bold', pad=20, color='#222222')
    
    # Wymuś liczby całkowite na osi X (lata)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    
    # Wymuś liczby całkowite na osi Y
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    
    # Ulepszony grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8, color='gray', zorder=0)
    ax.set_axisbelow(True)
    
    # Usuń górną i prawą ramkę
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Wartości nad słupkami z lepszym stylem
    for i, v in enumerate(liczby):
        ax.text(lata[i], v + (max(liczby) * 0.02), f'{v:,}'.replace(',', ' '), 
                ha='center', va='bottom', fontweight='bold', 
                fontsize=12, color='#222222')
    
    # Dodaj margines na górze
    ax.set_ylim(0, max(liczby) * 1.15)
    
    # Ustaw białe tło
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    
    # Zapisz do pamięci jako Base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=150, facecolor='white')
    img.seek(0)
    
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return plot_url

#WypadkiDrogowe
@main.route('/transportChart')
def transChart():
    wykres_base64 = utworz_wykres_base64()
    return render_template('transChart.html', wykres=wykres_base64)





def create_chart():
    # Pobierz dane z bazy
    conn = pyodbc.connect(connection_string_2)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM StatystykiWypadkow ORDER BY Lata")
    
    # Wczytaj dane
    rows = cursor.fetchall()
    conn.close()
    
    # Przygotuj dane do wykresu
    lata = [row[0] for row in rows]
    ilosc_wypadkow = [row[1] for row in rows]
    ilosc_zabitych = [row[2] for row in rows]
    ilosc_rannych = [row[3] for row in rows]
    
    # Utwórz wykres
    plt.figure(figsize=(14, 8))
    
    # Dodaj linie dla każdej serii danych
    plt.plot(lata, ilosc_wypadkow, marker='o', linewidth=2.5, 
             markersize=8, label='Liczba wypadków', color='#2E86AB')
    plt.plot(lata, ilosc_zabitych, marker='s', linewidth=2.5, 
             markersize=8, label='Liczba zabitych', color='#A23B72')
    plt.plot(lata, ilosc_rannych, marker='^', linewidth=2.5, 
             markersize=8, label='Liczba rannych', color='#F18F01')
    
    # Dostosuj wygląd wykresu
    plt.title('Statystyki wypadków drogowych (2014-2023)', 
              fontsize=20, fontweight='bold', pad=20)
    plt.xlabel('Rok', fontsize=14, fontweight='bold')
    plt.ylabel('Liczba', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=12, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(lata, rotation=45)
    plt.tight_layout()
    
    # Ustaw styl tła
    ax = plt.gca()
    ax.set_facecolor('#F8F9FA')
    plt.gcf().patch.set_facecolor('white')
    
    # Konwertuj wykres do base64
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=150, bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return plot_url

@main.route('/transChart12')
def transChart12():
    plot_url = create_chart()
    return render_template('transChart1.html', plot_url=plot_url)
