import sqlite3

def database_connect(db_path):
    """
    Получить connection к sqlite3 базе данных
    
    :param db_path: Путь к файлу .db
    """
    connection = sqlite3.connect(db_path)
    return connection