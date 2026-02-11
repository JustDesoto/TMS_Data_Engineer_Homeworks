import os
import pandas as pd

def top_profitable_genres(data_folder, output_folder, output_file="top_genres.xlsx"):
    invoice_items = pd.read_excel(os.path.join(data_folder, "invoice_items.xlsx"))
    tracks = pd.read_excel(os.path.join(data_folder, "tracks.xlsx")).drop(columns={"UnitPrice", "Name"})
    genres = pd.read_excel(os.path.join(data_folder, "genres.xlsx"))

    df = invoice_items.merge(tracks, on="TrackId").merge(genres, on="GenreId")
    df["Revenue"] = df["UnitPrice"] * df["Quantity"]
    result = df.groupby("Name")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False).head(5)

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_file)
    result.to_excel(output_path, index=False)
    print(f"Топ-5 прибыльных жанров сохранён в {output_path}")
