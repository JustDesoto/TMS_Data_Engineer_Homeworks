import os
import pandas as pd

def top_rock_customers(data_folder, output_folder, output_file="rock_customers.xlsx"):
    customers = pd.read_excel(os.path.join(data_folder, "customers.xlsx"))
    invoices = pd.read_excel(os.path.join(data_folder, "invoices.xlsx"))
    invoice_items = pd.read_excel(os.path.join(data_folder, "invoice_items.xlsx"))
    tracks = pd.read_excel(os.path.join(data_folder, "tracks.xlsx"))
    genres = pd.read_excel(os.path.join(data_folder, "genres.xlsx"))

    df = customers.merge(invoices, on="CustomerId") \
                .merge(invoice_items, on="InvoiceId") \
                .merge(tracks, on="TrackId") \
                .merge(genres, on="GenreId")
    rock_df = df[df["Name_y"] == "Rock"]
    result = rock_df.groupby(["CustomerId", "FirstName", "LastName"]).size().reset_index(name="RockPurchases")
    result = result.sort_values("RockPurchases", ascending=False)

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_file)
    result.to_excel(output_path, index=False)
    print(f"Клиенты с наибольшими покупками Rock сохранены в {output_path}")

