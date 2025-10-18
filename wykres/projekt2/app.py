from flask import Flask, render_template
import pyodbc
import matplotlib
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Konfiguracja połączenia z MSSQL
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=ALEKSANDRA;'  # Zmień na swoją nazwę serwera
        'DATABASE=WypadkiDrogowe;'
        'Trusted_Connection=yes;'
    )
    return conn

def create_chart():
    # Pobierz dane z bazy
    conn = get_db_connection()
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

@app.route('/')
def index():
    plot_url = create_chart()
    return render_template('index.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
