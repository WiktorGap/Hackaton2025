from flask import Flask, render_template
import pyodbc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import io
import base64


app = Flask(__name__)


def pobierz_dane_z_bazy():
    """Pobiera dane z bazy SQL Server"""
    server = 'localhost'
    database = 'WykroczeniaDrogowe'
    
    conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    
    try:
        conn = pyodbc.connect(conn_string)
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


@app.route('/')
def index():
    """Główna strona z wykresem"""
    wykres_base64 = utworz_wykres_base64()
    return render_template('index_base64.html', wykres=wykres_base64)


if __name__ == '__main__':
    app.run(debug=True)
