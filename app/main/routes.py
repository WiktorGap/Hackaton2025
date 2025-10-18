# from . import main
# from datetime import datetime, timezone
# from flask import render_template
# import pyodbc
# import base64
# import io
# import matplotlib
# matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# import pandas as pd

# connection_string_ = (
#     r'DRIVER={ODBC Driver 17 for SQL Server};'
#     r'SERVER=THINKBOOK_CODE;'
#     r'DATABASE=Hackaton;'
#     r'Trusted_Connection=yes;'
# )

# # KONFIGURACJA WYKRESÓW DLA KONKRETNYCH TABEL
# CHART_CONFIGS = {
#     '2.1. Powierzchnia i ludność średnik': {
#         'time_series': [
#             {
#                 'x_column': 'Lata',
#                 'y_column': 'Ludnosc_ogolem', 
#                 'title': 'Ludność na przestrzeni lat',
#                 'color': 'blue',
#                 'line_style': '-'
#             },
#             {
#                 'x_column': 'Lata',
#                 'y_column': 'Kobiety_na_100_mezczyzn',
#                 'title': 'Liczba kobiet na 100 mężczyzn na przestrzeni lat',
#                 'color': 'red', 
#                 'line_style': '-'
#             },
#             {
#                 'x_column': 'Lata',
#                 'y_column': 'Ludnosc_na_1_km_kw',
#                 'title': 'Zagęszczenie ludności na 1km² na przestrzeni lat',
#                 'color': 'green',
#                 'line_style': '-'
#             },
#             {
#                 'x_column': 'Lata', 
#                 'y_column': 'Obszar_km_kw',
#                 'title': 'Obszar miasta na przestrzeni lat',
#                 'color': 'purple',
#                 'line_style': '-'
#             }
#         ],
#         'multi_line': [
#             {
#                 'x_column': 'Lata',
#                 'y_columns': ['mezczyzni_udzial_w', 'kobiety_udzial_w'],
#                 'colors': ['blue', 'red'],
#                 'labels': ['Mężczyźni', 'Kobiety'],
#                 'title': 'Stosunek procentowy kobiet i mężczyzn w społeczeństwie Płocka na przestrzeni lat'
#             }
#         ]
#     },
#     '2.5. Pojedyncze roczniki średnik': {
#         'multi_line': [
#             {
#                 'x_column': 'Wiek',
#                 'y_columns': ['kobiety', 'mezczyzni'],
#                 'colors': ['red', 'blue'],
#                 'labels': ['Kobiety', 'Mężczyźni'],
#                 'title': 'Wiek populacji w społeczeństwie w podziale na płeć'
#             }
#         ]
#     }
#     # Tabela "2.4. Ruch naturalny w Płocku średnik" będzie używać domyślnego generowania wykresów
# }

# @main.route('/', methods=['GET', 'POST'])
# def index():
#     current_time = datetime.now(timezone.utc)
#     return render_template('base.html', current_time=current_time)

# @main.route('/data', methods=['GET'])
# def displayData():
#     try:
#         con = pyodbc.connect(connection_string_)
#         print("Connection established successfully.")
        
#         cursor = con.cursor()
#         cursor.execute("""
#             SELECT TABLE_NAME 
#             FROM INFORMATION_SCHEMA.TABLES 
#             WHERE TABLE_TYPE = 'BASE TABLE'
#         """)
#         tables = [row[0] for row in cursor.fetchall()]
        
#         charts_data = []
        
#         for table_name in tables:
#             print(f"Processing table: {table_name}")
            
#             df = pd.read_sql(f"SELECT * FROM [{table_name}]", con)
            
#             if len(df) > 0:
#                 table_charts = generate_charts_for_table(df, table_name)
#                 charts_data.extend(table_charts)
        
#         cursor.close()
#         con.close()
        
#         return render_template('data_display.html', charts_data=charts_data)
        
#     except Exception as e:
#         print(f"Connection error: {e}")
#         return render_template('data_display.html', charts_data=[], error=str(e))

# def generate_charts_for_table(df, table_name):
#     """Generuje wykresy dla danej tabeli według predefiniowanych reguł"""
#     charts = []
    
#     # Sprawdź czy istnieje konfiguracja dla tej tabeli
#     if table_name in CHART_CONFIGS:
#         config = CHART_CONFIGS[table_name]
#         charts.extend(generate_configured_charts(df, table_name, config))
#     else:
#         # Domyślne generowanie wykresów jeśli nie ma konfiguracji
#         charts.extend(generate_default_charts(df, table_name))
    
#     return charts

# def generate_configured_charts(df, table_name, config):
#     """Generuje wykresy według specyficznej konfiguracji tabeli"""
#     charts = []
    
#     # Pojedyncze wykresy liniowe (time series)
#     if 'time_series' in config:
#         for chart_config in config['time_series']:
#             x_col = chart_config['x_column']
#             y_col = chart_config['y_column']
#             title = chart_config['title']
#             color = chart_config.get('color', 'blue')
#             line_style = chart_config.get('line_style', '-')
            
#             if x_col in df.columns and y_col in df.columns:
#                 chart = create_line_chart(df, x_col, y_col, table_name, title, color, line_style)
#                 if chart:
#                     charts.append(chart)
    
#     # Wykresy z wieloma liniami na jednym wykresie
#     if 'multi_line' in config:
#         for multi_config in config['multi_line']:
#             x_col = multi_config['x_column']
#             y_cols = multi_config['y_columns']
#             title = multi_config['title']
#             colors = multi_config.get('colors', ['blue', 'red', 'green', 'orange'])
#             labels = multi_config.get('labels', y_cols)
            
#             if x_col in df.columns and all(y_col in df.columns for y_col in y_cols):
#                 chart = create_multi_line_chart(df, x_col, y_cols, table_name, title, colors, labels)
#                 if chart:
#                     charts.append(chart)
    
#     # Wykresy słupkowe
#     if 'bar_charts' in config:
#         for bar_config in config['bar_charts']:
#             if 'x_column' in bar_config and 'y_column' in bar_config:
#                 x_col = bar_config['x_column']
#                 y_col = bar_config['y_column']
#                 title = bar_config.get('title', f'{y_col} vs {x_col}')
                
#                 if x_col in df.columns and y_col in df.columns:
#                     chart = create_bar_chart(df, x_col, y_col, table_name, title)
#                     if chart:
#                         charts.append(chart)
#             elif 'column' in bar_config:
#                 col = bar_config['column']
#                 title = bar_config.get('title', col)
                
#                 if col in df.columns:
#                     chart = create_simple_bar_chart(df, col, table_name, title)
#                     if chart:
#                         charts.append(chart)
    
#     return charts

# def generate_default_charts(df, table_name):
#     """Domyślne generowanie wykresów gdy nie ma specyficznej konfiguracji"""
#     charts = []
#     numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
#     # Jeśli mamy kolumnę 'Lata' i kolumny numeryczne
#     if 'Lata' in df.columns and len(numeric_columns) > 0:
#         for col in numeric_columns:
#             if col != 'Lata':
#                 chart = create_line_chart(df, 'Lata', col, table_name, f'{col} w czasie')
#                 if chart:
#                     charts.append(chart)
    
#     return charts

# def create_line_chart(df, x_col, y_col, table_name, title, color='blue', line_style='-'):
#     """Tworzy wykres liniowy"""
#     try:
#         plt.figure(figsize=(12, 7))
#         plt.plot(df[x_col], df[y_col], marker='o', linewidth=2.5, 
#                 markersize=6, color=color, linestyle=line_style)
#         plt.title(title, fontsize=16, fontweight='bold', pad=20)
#         plt.xlabel(x_col, fontsize=12)
#         plt.ylabel(y_col, fontsize=12)
#         plt.grid(True, alpha=0.3)
#         plt.xticks(rotation=45)
#         plt.tight_layout()
        
#         return save_chart_to_base64(table_name, title)
#     except Exception as e:
#         print(f"Error creating line chart for {y_col}: {e}")
#         plt.close()
#         return None

# def create_multi_line_chart(df, x_col, y_cols, table_name, title, colors, labels):
#     """Tworzy wykres z wieloma liniami"""
#     try:
#         plt.figure(figsize=(12, 7))
        
#         for i, y_col in enumerate(y_cols):
#             color = colors[i % len(colors)]
#             label = labels[i % len(labels)]
#             plt.plot(df[x_col], df[y_col], marker='o', linewidth=2.5, 
#                     markersize=6, color=color, label=label)
        
#         plt.title(title, fontsize=16, fontweight='bold', pad=20)
#         plt.xlabel(x_col, fontsize=12)
#         plt.ylabel('Liczba ludności', fontsize=12)
#         plt.grid(True, alpha=0.3)
#         plt.legend(loc='best')
#         plt.xticks(rotation=45)
#         plt.tight_layout()
        
#         return save_chart_to_base64(table_name, title)
#     except Exception as e:
#         print(f"Error creating multi-line chart: {e}")
#         plt.close()
#         return None

# def create_bar_chart(df, x_col, y_col, table_name, title):
#     """Tworzy wykres słupkowy"""
#     try:
#         plt.figure(figsize=(12, 7))
#         plt.bar(df[x_col], df[y_col], alpha=0.7, color='skyblue')
#         plt.title(title, fontsize=16, fontweight='bold', pad=20)
#         plt.xlabel(x_col, fontsize=12)
#         plt.ylabel(y_col, fontsize=12)
#         plt.grid(True, alpha=0.3)
#         plt.xticks(rotation=45)
#         plt.tight_layout()
        
#         return save_chart_to_base64(table_name, title)
#     except Exception as e:
#         print(f"Error creating bar chart: {e}")
#         plt.close()
#         return None

# def create_simple_bar_chart(df, column, table_name, title):
#     """Tworzy prosty wykres słupkowy"""
#     try:
#         plt.figure(figsize=(10, 6))
#         plt.bar(range(len(df)), df[column], color='lightcoral', alpha=0.7)
#         plt.title(f'{table_name}\n{title}', fontsize=14, fontweight='bold')
#         plt.xlabel('Index')
#         plt.ylabel(column)
#         plt.grid(True, alpha=0.3)
#         plt.tight_layout()
        
#         return save_chart_to_base64(table_name, title)
#     except Exception as e:
#         print(f"Error creating simple bar chart: {e}")
#         plt.close()
#         return None

# def save_chart_to_base64(table_name, chart_name):
#     """Zapisuje aktualny wykres do base64 i zamyka figure"""
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
#     buf.seek(0)
#     chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()
#     plt.close()
    
#     return {
#         'table_name': table_name,
#         'chart_name': chart_name,
#         'chart_data': chart_base64
#     }

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

@main.route('/', methods=['GET', 'POST'])
def index():
    current_time = datetime.now(timezone.utc)
    return render_template('base.html', current_time=current_time)

@main.route('/data', methods=['GET'])
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
        # Dynamiczne dostosowanie szerokości wykresu w zależności od liczby punktów danych
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
        
        # Ustawienie etykiet osi X z odpowiednimi odstępami
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