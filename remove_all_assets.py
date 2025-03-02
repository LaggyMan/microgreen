from tb_rest_client.rest_client_pe import RestClientPE
from tb_rest_client.rest import ApiException
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

# Получение всех ассетов
try:
    assets = rest_client.get_tenant_assets(page_size=1000, page=0).data
    print(f"Найдено ассетов: {len(assets)}")

    # Удаление каждого ассета
    for asset in assets:
        rest_client.delete_asset(asset_id=asset.id.id)
        print(f"Удален ассет: {asset.name}")

    print("Все ассеты удалены.")
except ApiException as e:
    print(f"Ошибка при удалении ассетов: {e}")