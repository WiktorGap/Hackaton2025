import pandas as pd
import os
from collections import Counter
import pyodbc




FILE_STORAGE_PATH = os.path.join(os.getcwd(), "file_storage")

def getFiles():
    files = []
    if os.path.isdir(FILE_STORAGE_PATH):
        for file in os.listdir(FILE_STORAGE_PATH):
            if file.lower().endswith('.csv'):
                files.append(os.path.join(FILE_STORAGE_PATH, file))
    return files


def connection():
    try:
        con = pyodbc.connect(connection_string_)
        print("Connection established successfully.")
        return con
    except Exception as e:
        print(f"Connection error: {e}")
        return None


connection_string_ = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=THINKBOOK_CODE;'
    r'DATABASE=Hackaton;'
    r'Trusted_Connection=yes;'
)










def make_columns_unique(columns):
    """Dodaje sufiksy .1, .2 do duplikatów kolumn"""
    counts = Counter()
    new_columns = []
    for col in columns:
        if counts[col] == 0:
            new_columns.append(col)
        else:
            new_columns.append(f"{col}.{counts[col]}")
        counts[col] += 1
    return new_columns

def proccessFiles():
    files = getFiles()
    subFileDict = {}

    for filePath in files:
        # Wczytanie CSV ze średnikiem
        df = pd.read_csv(filePath, sep=';')

        # Upewnienie się, że kolumny są unikalne
        df.columns = make_columns_unique(df.columns)

        # Poprawa formatu liczb: usuwanie spacji i zamiana przecinka na kropkę
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.replace(' ', '', regex=False)  # usuwa niełamliwe spacje
                df[col] = df[col].str.replace(' ', '', regex=False)   # usuwa zwykłe spacje
                df[col] = df[col].str.replace(',', '.', regex=False)  # zamiana przecinka na kropkę
                # próba konwersji do liczby
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass  # zostaje tekst, jeśli nie da się konwertować

        # Dodatkowo możemy wymusić, żeby kolumny typu liczbowego były int lub float
        for col in df.columns:
            if pd.api.types.is_float_dtype(df[col]):
                df[col] = df[col].astype(float)
            elif pd.api.types.is_integer_dtype(df[col]):
                df[col] = df[col].astype(int)

        # Zamiana DataFrame na listę słowników
        records = df.to_dict(orient='records')
        # Dodanie do głównego słownika pod nazwą pliku
        subFileDict[os.path.basename(filePath)] = records

    return subFileDict










if __name__ == "__main__":
    data = proccessFiles()
    for file, records in data.items():
        print(f"{file}: {len(records)} rekordów")
        print(records)  # pokaż dwa pierwsze rekordy
