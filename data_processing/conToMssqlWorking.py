import pandas as pd
import os
import pyodbc
import re

FILE_STORAGE_PATH = os.path.join(os.getcwd(), "file_storage")

connection_string_ = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=THINKBOOK_CODE;'
    r'DATABASE=Hackaton;'
    r'Trusted_Connection=yes;'
)

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

def pandas_to_sql_dtype(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "BIGINT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BIT"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATETIME"
    else:
        return "NVARCHAR(MAX)"

def clean_column_name(col):
    col = col.strip()
    col = re.sub(r'[^0-9a-zA-Z_]', '_', col)  # Replace non-alphanumeric characters with _
    col = re.sub(r'_+', '_', col)  # Replace multiple underscores with single
    col = col.strip('_')  # Remove leading/trailing underscores
    return col[:128]  # Truncate to 128 characters

def convert_numeric_columns(df):
    """Convert comma decimals to dot decimals and convert numeric columns to float/int"""
    for col in df.columns:
        if df[col].dtype == object:
            try:
                # Try to convert to numeric, replacing comma with dot
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='ignore')
            except Exception:
                pass
    return df

def saveDataToDb():
    files = getFiles()
    con = connection()
    if not con:
        return

    cursor = con.cursor()
    cursor.fast_executemany = True

    for file_path in files:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"Processing file: {file_name}")

        try:
            # Read CSV with semicolon separator
            df = pd.read_csv(file_path, sep=';', encoding='utf-8')
            print(f"Original columns: {df.columns.tolist()}")
            
            # Clean column names
            df.columns = [clean_column_name(col) for col in df.columns]
            print(f"Cleaned columns: {df.columns.tolist()}")
            
            # Convert numeric columns
            df = convert_numeric_columns(df)
            
            # Drop table if it exists and create new one
            drop_table_sql = f"IF OBJECT_ID('{file_name}', 'U') IS NOT NULL DROP TABLE [{file_name}]"
            cursor.execute(drop_table_sql)
            con.commit()
            
            # Create table with proper columns
            columns_sql = [f"[{col}] {pandas_to_sql_dtype(dtype)}" for col, dtype in zip(df.columns, df.dtypes)]
            create_table_sql = f"CREATE TABLE [{file_name}] ({', '.join(columns_sql)})"
            cursor.execute(create_table_sql)
            con.commit()
            print(f"Table {file_name} created successfully.")

            # Insert data
            placeholders = ','.join(['?' for _ in df.columns])
            insert_sql = f"INSERT INTO [{file_name}] ({', '.join(f'[{col}]' for col in df.columns)}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples for executemany
            data_tuples = [tuple(x) for x in df.to_numpy()]
            cursor.executemany(insert_sql, data_tuples)
            con.commit()
            
            print(f"Data from {file_name}.csv inserted successfully. Rows affected: {len(df)}")
            
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            con.rollback()

    cursor.close()
    con.close()






if __name__ == "__main__":
    saveDataToDb()