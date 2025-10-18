from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

# Konfiguracja połączenia z bazą danych MSSQL
SERVER = 'localhost'  # Zmień na swój serwer
DATABASE = 'master'   # Zmień na swoją bazę
USERNAME = 'ALEKSANDRA'       # Zmień na swojego użytkownika
# PASSWORD = 'hasło'    # Zmień na swoje hasło

# Definicja baz danych i ich struktur
DATABASES = {
    'BezrobotniDB': {
        'table': 'Bezrobotni',
        'columns': ['id', 'ogolem', 'kobiety', 'mezczyzni']
    },
    'ImprezKulturalneDB': {
        'table': 'ImprezKulturalne',
        'columns': ['id', 'rok', 'liczbaimprez', 'liczbauczestnikow']
    },
    'WypadkiDrogoweDB': {
        'table': 'WypadkiDrogowe',
        'columns': ['id', 'lata', 'iloscwypadkow', 'ilosczabitych', 'iloscrannych', 
                   'kierowcysamochodowosobowych', 'kierowcysamochodowciezarowych', 
                   'kierowcyinnych', 'piesi']
    },
    'WykroczeniaDB': {
        'table': 'Wykroczenia',
        'columns': ['id', 'wyszczególnienie', 'rok2020', 'rok2021', 'rok2022', 'rok2023']
    }
}

def get_db_connection(database_name):
    """Tworzy połączenie z bazą danych"""
    try:
        connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={SERVER};'
            f'DATABASE={database_name};'
            f'UID={USERNAME};'
            f'PWD={PASSWORD}'
        )
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return None

def fetch_data(database_name, table_name, columns):
    """Pobiera dane z wybranej bazy danych i tabeli"""
    conn = get_db_connection(database_name)
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        columns_str = ', '.join(columns)
        query = f"SELECT {columns_str} FROM {table_name}"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        conn.close()
        return data
    except Exception as e:
        print(f"Błąd zapytania: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    """Główna strona z formularzem"""
    data = None
    selected_db = None
    selected_table = None
    selected_columns = None
    error = None
    
    if request.method == 'POST':
        selected_db = request.form.get('database')
        selected_table = request.form.get('table')
        selected_columns_list = request.form.getlist('columns')
        
        if selected_db and selected_table and selected_columns_list:
            db_info = DATABASES.get(selected_db)
            if db_info and db_info['table'] == selected_table:
                data = fetch_data(selected_db, selected_table, selected_columns_list)
                selected_columns = selected_columns_list
                if data is None:
                    error = "Błąd podczas pobierania danych z bazy"
            else:
                error = "Nieprawidłowy wybór bazy lub tabeli"
        else:
            error = "Proszę wypełnić wszystkie pola formularza"
    
    return render_template('index.html', 
                         databases=DATABASES,
                         data=data,
                         selected_db=selected_db,
                         selected_table=selected_table,
                         selected_columns=selected_columns,
                         error=error)

if __name__ == '__main__':
    app.run(debug=True)
