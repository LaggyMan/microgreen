from tb_rest_client.rest_client_pe import RestClientPE
from tb_rest_client.rest import ApiException
import csv
import json

# Загрузка настроек из JSON
with open("config.json", "r") as config_file:
    config = json.load(config_file)

THINGSBOARD_URL = config["thingsboard_url"]
USERNAME = config["username"]
PASSWORD = config["password"]

# Подключение к ThingsBoard
rest_client = RestClientPE(base_url=THINGSBOARD_URL)
rest_client.login(username=USERNAME, password=PASSWORD)

# Чтение данных из CSV
with open("cities_and_farms.csv", mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    data = list(reader)

# Создание ассетов (городов) и ассетов (ферм)
for row in data:
    city_name = row["city"]
    farm_name = row["farm_name"]

    # Создаем ассет (город), если он еще не создан
    city_asset = rest_client.get_tenant_assets(page_size=10, page=0, text_search=city_name).data
    if not city_asset:
        city_asset = {
            "name": city_name,
            "type": "city",
            "additionalInfo": {
                "latitude": float(row["city_lat"]),
                "longitude": float(row["city_lon"])
            }
        }
        created_city = rest_client.save_asset(body=city_asset)
        print(f"Создан ассет (город): {created_city.name}")
    else:
        created_city = city_asset[0]

    # Создаем ассет (ферма)
    farm_asset = {
        "name": farm_name,
        "type": "farm",
        "additionalInfo": {
            "latitude": float(row["farm_lat"]),
            "longitude": float(row["farm_lon"])
        }
    }
    created_farm = rest_client.save_asset(body=farm_asset)
    print(f"Создан ассет (ферма): {created_farm.name}")

    # Связываем ферму с городом
    relation = {
        "from": {"id": created_city.id.id, "entityType": "ASSET"},
        "to": {"id": created_farm.id.id, "entityType": "ASSET"},
        "type": "Contains"
    }
    rest_client.save_relation(body=relation)
    print(f"Ферма {created_farm.name} связана с городом {created_city.name}")

print("Генерация завершена!")