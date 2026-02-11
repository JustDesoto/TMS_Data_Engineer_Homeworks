import os
import pandas as pd
import sqlite3

def database_export(connection: sqlite3.Connection, output_folder):
    """
    Экспорт всех баз, хранящихся в базе данных в формате .xlsx
    
    :param connection: Connection к базе данных, из которой будет осуществляться выгрузка
    :type connection: sqlite3.Connection
    :param output_folder: Папка, в которую будут выгружаться таблицы
    """
    cursor = connection.cursor()

    os.makedirs(output_folder, exist_ok=True)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for (table_name,) in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", connection)
        output_path = os.path.join(output_folder, f"{table_name}.xlsx")
        df.to_excel(output_path, index=False)
        print(f"Таблица {table_name} сохранена в {output_path}")
    connection.close()
