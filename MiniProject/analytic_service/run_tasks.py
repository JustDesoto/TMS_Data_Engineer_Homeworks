import os
import sqlite3
from analytic_service.analytic_tasks.avg_duration import avg_duration_by_genre
from analytic_service.analytic_tasks.tracks_albums_artists import tracks_with_album_artist
from analytic_service.analytic_tasks.top_genres import top_profitable_genres
from analytic_service.analytic_tasks.rock_customers import top_rock_customers


def run_all_tasks(connection: sqlite3.Connection, output_folder, data_folder):
    """
    Запуск всех аналитических тасок
    
    :param connection: connection
    :type connection: sqlite3.Connection
    :param output_folder: Папка, в которую осуществляется выгрузка аналитических данных
    :param data_folder: Папка, в которой хранятся таблицы в формате .xlsx
    """

    os.makedirs(output_folder, exist_ok=True)

    avg_duration_by_genre(data_folder,output_folder)
    tracks_with_album_artist(data_folder,output_folder)
    top_profitable_genres(data_folder,output_folder)
    top_rock_customers(data_folder,output_folder)

    connection.close()
