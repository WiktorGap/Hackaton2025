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
# import numpy as np

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
#                 'title': 'Wiek populacji w społeczeństwie w podziale na płeć',
#                 'x_ticks_step': 5,  # Pokazuj co 5 rok
#                 'width_scale': 1.5  # Szerokość wykresu
#             }
#         ]
#     }
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
#             x_ticks_step = multi_config.get('x_ticks_step')
#             width_scale = multi_config.get('width_scale', 1.0)
            
#             if x_col in df.columns and all(y_col in df.columns for y_col in y_cols):
#                 chart = create_multi_line_chart(df, x_col, y_cols, table_name, title, colors, labels, x_ticks_step, width_scale)
#                 if chart:
#                     charts.append(chart)
    
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

# def create_multi_line_chart(df, x_col, y_cols, table_name, title, colors, labels, x_ticks_step=None, width_scale=1.0):
#     """Tworzy wykres z wieloma liniami"""
#     try:
#         # Dynamiczne dostosowanie szerokości wykresu w zależności od liczby punktów danych
#         base_width = 12
#         calculated_width = max(base_width, len(df) * 0.15) * width_scale
#         plt.figure(figsize=(calculated_width, 7))
        
#         for i, y_col in enumerate(y_cols):
#             color = colors[i % len(colors)]
#             label = labels[i % len(labels)]
#             plt.plot(df[x_col], df[y_col], marker='o', linewidth=2, 
#                     markersize=4, color=color, label=label, alpha=0.8)
        
#         plt.title(title, fontsize=16, fontweight='bold', pad=20)
#         plt.xlabel(x_col, fontsize=12)
#         plt.ylabel('Liczba ludności', fontsize=12)
#         plt.grid(True, alpha=0.3)
#         plt.legend(loc='best')
        
#         # Ustawienie etykiet osi X z odpowiednimi odstępami
#         if x_ticks_step is not None and len(df) > x_ticks_step:
#             # Pokazuj tylko co x-tą etykietę
#             ticks = df[x_col][::x_ticks_step]
#             plt.xticks(ticks, rotation=45, fontsize=10)
#         else:
#             # Dla mniejszej liczby punktów pokazuj wszystkie etykiety
#             plt.xticks(rotation=45, fontsize=10)
        
#         # Zwiększ odstępy między subplotami aby zmieścić etykiety
#         plt.tight_layout(pad=3.0)
        
#         return save_chart_to_base64(table_name, title)
#     except Exception as e:
#         print(f"Error creating multi-line chart: {e}")
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




























# def get_budget_data():
#     """Pobiera dane z tabeli Budzet z bazy danych"""
#     try:
#         conn = pyodbc.connect(connection_string_)
#         query = "SELECT [Miasto], [Zplanowana kwota], [na mieszkańca], [Zgłoszone projekty], [Głosujący na projekty] FROM [Hackaton].[dbo].[Budzet]"
#         df = pd.read_sql(query, conn)
#         conn.close()
        
#         # Konwersja danych na właściwe typy
#         df['Zplanowana kwota'] = pd.to_numeric(df['Zplanowana kwota'], errors='coerce')
#         df['na mieszkańca'] = pd.to_numeric(df['na mieszkańca'], errors='coerce')
#         df['Zgłoszone projekty'] = pd.to_numeric(df['Zgłoszone projekty'], errors='coerce')
#         df['Głosujący na projekty'] = pd.to_numeric(df['Głosujący na projekty'], errors='coerce')
        
#         return df
#     except Exception as e:
#         print(f"Błąd podczas pobierania danych: {e}")
#         return None

# def create_bar_chart(df):
#     """Tworzy wykres słupkowy - zaplanowane kwoty według miast"""
#     plt.figure(figsize=(14, 8))
    
#     # Sortowanie danych dla lepszej czytelności
#     df_sorted = df.sort_values('Zplanowana kwota', ascending=False)
    
#     bars = plt.bar(df_sorted['Miasto'], df_sorted['Zplanowana kwota'] / 1000000, 
#                    color='skyblue', edgecolor='navy', alpha=0.7)
    
#     plt.title('Zaplanowane kwoty budżetu obywatelskiego w miastach', 
#               fontsize=16, fontweight='bold', pad=20)
#     plt.xlabel('Miasta', fontsize=12)
#     plt.ylabel('Zaplanowana kwota (mln zł)', fontsize=12)
#     plt.xticks(rotation=45, ha='right')
#     plt.grid(axis='y', alpha=0.3)
    
#     # Dodanie wartości na słupkach
#     for bar in bars:
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width()/2., height,
#                 f'{height:.1f}M',
#                 ha='center', va='bottom', fontsize=9)
    
#     plt.tight_layout()
    
#     # Konwersja do base64
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
#     buf.seek(0)
#     chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()
#     plt.close()
    
#     return chart_base64

# def create_pie_chart(df):
#     """Tworzy wykres kołowy - udział miast w liczbie głosujących"""
#     plt.figure(figsize=(10, 10))
    
#     # Sortowanie i wybór top 8 miast + pozostałe
#     df_sorted = df.sort_values('Głosujący na projekty', ascending=False)
#     top_cities = df_sorted.head(8)
#     others_sum = df_sorted.iloc[8:]['Głosujący na projekty'].sum()
    
#     # Przygotowanie danych dla wykresu kołowego
#     labels = list(top_cities['Miasto']) + ['Pozostałe miasta']
#     sizes = list(top_cities['Głosujący na projekty']) + [others_sum]
    
#     # Kolory
#     colors = plt.cm.Set3(range(len(labels)))
    
#     # Tworzenie wykresu kołowego
#     wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
#                                        startangle=90, textprops={'fontsize': 10})
    
#     # Poprawa wyglądu procentów
#     for autotext in autotexts:
#         autotext.set_color('black')
#         autotext.set_fontweight('bold')
    
#     plt.title('Udział miast w liczbie głosujących na projekty', 
#               fontsize=16, fontweight='bold', pad=20)
#     plt.axis('equal')  # Zapewnia, że wykres jest okrągły
    
#     plt.tight_layout()
    
#     # Konwersja do base64
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
#     buf.seek(0)
#     chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()
#     plt.close()
    
#     return chart_base64

# def create_projects_per_capita_chart(df):
#     """Tworzy wykres słupkowy - projekty na 100k mieszkańców"""
#     plt.figure(figsize=(14, 8))
    
#     # Sortowanie danych
#     df_sorted = df.sort_values('Zgłoszone projekty', ascending=False)
    
#     bars = plt.bar(df_sorted['Miasto'], df_sorted['Zgłoszone projekty'], 
#                    color='lightcoral', edgecolor='darkred', alpha=0.7)
    
#     plt.title('Liczba zgłoszonych projektów na 100 tysięcy mieszkańców', 
#               fontsize=16, fontweight='bold', pad=20)
#     plt.xlabel('Miasta', fontsize=12)
#     plt.ylabel('Liczba projektów na 100k mieszkańców', fontsize=12)
#     plt.xticks(rotation=45, ha='right')
#     plt.grid(axis='y', alpha=0.3)
    
#     # Dodanie wartości na słupkach
#     for bar in bars:
#         height = bar.get_height()
#         plt.text(bar.get_x() + bar.get_width()/2., height,
#                 f'{height:.0f}',
#                 ha='center', va='bottom', fontsize=9)
    
#     plt.tight_layout()
    
#     # Konwersja do base64
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
#     buf.seek(0)
#     chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
#     buf.close()
#     plt.close()
    
#     return chart_base64

# @main.route('/budget',methods=['GET'])
# def display_budget_charts():
#     """Główna trasa wyświetlająca wykresy budżetowe"""
#     df = get_budget_data()
    
#     if df is None or df.empty:
#         return render_template('budget_charts.html', 
#                              error="Nie udało się pobrać danych z bazy",
#                              charts=[])
    
#     # Generowanie wykresów
#     charts = []
    
#     # Wykres 1: Słupkowy - zaplanowane kwoty
#     bar_chart = create_bar_chart(df)
#     charts.append({
#         'title': 'Zaplanowane kwoty budżetu obywatelskiego',
#         'description': 'Porównanie zaplanowanych kwot budżetu obywatelskiego w milionach złotych',
#         'chart_data': bar_chart
#     })
    
#     # Wykres 2: Kołowy - udział w głosujących
#     pie_chart = create_pie_chart(df)
#     charts.append({
#         'title': 'Udział miast w liczbie głosujących',
#         'description': 'Procentowy udział miast w ogólnej liczbie głosujących na projekty',
#         'chart_data': pie_chart
#     })
    
#     # Wykres 3: Słupkowy - projekty na 100k mieszkańców
#     projects_chart = create_projects_per_capita_chart(df)
#     charts.append({
#         'title': 'Liczba projektów na 100 tysięcy mieszkańców',
#         'description': 'Aktywność mieszkańców mierzona liczbą zgłoszonych projektów',
#         'chart_data': projects_chart
#     })
    
#     # Dodatkowe statystyki
#     stats = {
#         'total_cities': len(df),
#         'total_budget': f"{df['Zplanowana kwota'].sum() / 1000000:.1f}",
#         'avg_budget_per_capita': f"{df['na mieszkańca'].mean():.1f}",
#         'total_voters': f"{df['Głosujący na projekty'].sum():,}".replace(',', ' ')
#     }
    
#     return render_template('budget_charts.html', charts=charts, stats=stats, error=None)



