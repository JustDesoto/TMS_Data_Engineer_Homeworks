import os
import pandas as pd

def avg_duration_by_genre(data_folder, output_folder, output_file="avg_duration.xlsx"):
    tracks = pd.read_excel(os.path.join(data_folder, "tracks.xlsx"))
    genres = pd.read_excel(os.path.join(data_folder, "genres.xlsx"))

    df = tracks.merge(genres, left_on="GenreId", right_on="GenreId").rename(columns={"Name_y" : "Name"})
    result = df.groupby("Name")["Milliseconds"].mean().reset_index()

    output_path = os.path.join(output_folder, output_file)
    result.to_excel(output_path, index=False)
    print(f"Средняя длительность по жанрам сохранена в {output_path}")
