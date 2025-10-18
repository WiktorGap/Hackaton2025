from . import main
from datetime import datetime, timezone
from flask import render_template
import pyodbc
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

connection_string_ = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=THINKBOOK_CODE;'
    r'DATABASE=Hackaton;'
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



@main.route('/')
def index():
    return render_template('base.html')





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
