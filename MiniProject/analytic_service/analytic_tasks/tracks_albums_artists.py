import os
import pandas as pd

def tracks_with_album_artist(data_folder, output_folder, output_file="tracks_albums_artists.xlsx"):
    tracks = pd.read_excel(os.path.join(data_folder, "tracks.xlsx"))
    albums = pd.read_excel(os.path.join(data_folder, "albums.xlsx"))
    artists = pd.read_excel(os.path.join(data_folder, "artists.xlsx"))

    df = tracks.merge(albums, on="AlbumId").merge(artists, on="ArtistId")
    result = df[["Name_x", "Title", "Name_y"]].rename(columns={"Name_x" : "TrackName", "Name_y" : "Artist"})

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_file)
    result.to_excel(output_path, index=False)
    print(f"Треки с альбомами и артистами сохранены в {output_path}")
