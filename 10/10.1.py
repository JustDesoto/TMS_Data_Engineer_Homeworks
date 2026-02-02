# Было
#  files = ["10/data_2023_01.txt", "10/data_2023_02.txt", "10/data_2023_03.txt"]


# Стало
data = {
    "data_2023_01.txt": [
        "2023-01-01:1000:Иван Иванов",
        "2023-01-02:1500:Петр Петров",
        "2023-01-02:2000:Мария Сидорова",
    ],
    "data_2023_02.txt": [
        "2023-02-01:2000:Иван Иванов",
        "2023-02-02:1800:Петр Петров",
        "2023-02-03:2200:Мария Сидорова",
    ],
    "data_2023_03.txt": [
        "2023-03-01:2100:Мария Сидорова",
        "2023-03-02:1300:Иван Иванов",
        "2023-03-03:1700:Петр Петров",
    ]
}

for filename, lines in data.items():
    with open(f"10/{filename}", "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")

manager_sales = {}
total_sales = 0


for date_file in data:
    with open(f"10/{date_file}", "r", encoding="utf-8") as file:
        for line in file:
            date, amount, manager = line.strip().split(":")
            amount = int(amount)
            total_sales += amount

            if manager not in manager_sales:
                manager_sales[manager] = 0
            manager_sales[manager] += amount

            # print(manager_sales.items())


        best_manager = max(manager_sales,key=manager_sales.get)
        best_manager_sales = manager_sales[best_manager]


with open("10/report.txt", "w", encoding="utf-8") as file:
    file.write(f"Общая сумма продаж: {total_sales}\n")
    file.write(f"Лучший менеджер: {best_manager}")