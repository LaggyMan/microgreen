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

# Получение списка городов и ферм
cities = rest_client.get_tenant_assets(page_size=1000, page=0, type="city").data
farms = rest_client.get_tenant_assets(page_size=1000, page=0, type="farm").data

# Создание основного дашборда
dashboard = {
    "title": "Фермы микрозелени",
    "configuration": {
        "description": "Дашборд для мониторинга ферм микрозелени",
        "states": {
            "default": {
                "name": "Города",
                "root": True
            }
        },
        "widgets": {},
        "entityAliases": {},
        "layouts": {
            "main": {
                "widgets": [],
                "gridSettings": {
                    "backgroundColor": "#ffffff",
                    "columns": 24,
                    "margin": 10,
                    "backgroundSizeMode": "100%"
                }
            }
        }
    }
}

# Добавление виджета карты для городов
city_map_widget = {
    "type": "map",
    "title": "Карта городов",
    "config": {
        "mapProvider": "openstreetmap",
        "latitude": 55.7558,  # Центр карты (Москва)
        "longitude": 37.6176,
        "zoomLevel": 4,
        "markers": []
    }
}

# Добавление маркеров для городов
for city in cities:
    city_info = city["additionalInfo"]
    marker = {
        "latitude": city_info["latitude"],
        "longitude": city_info["longitude"],
        "tooltip": f"Город: {city['name']}",
        "actions": {
            "onClick": {
                "state": city["name"],  # Переход в состояние города
                "target": "default"  # Основное состояние
            }
        }
    }
    city_map_widget["config"]["markers"].append(marker)

# Добавление виджета карты на основной дашборд
dashboard["configuration"]["widgets"]["city_map"] = city_map_widget
dashboard["configuration"]["layouts"]["main"]["widgets"].append({
    "id": "city_map",
    "row": 0,
    "col": 0,
    "sizeX": 24,
    "sizeY": 12
})

# Создание состояний для городов
for city in cities:
    city_state = {
        "name": city["name"],
        "root": False,
        "widgets": {},
        "layouts": {
            "main": {
                "widgets": [],
                "gridSettings": {
                    "backgroundColor": "#ffffff",
                    "columns": 24,
                    "margin": 10,
                    "backgroundSizeMode": "100%"
                }
            }
        }
    }

    # Добавление виджета карты для ферм города
    farm_map_widget = {
        "type": "map",
        "title": f"Карта ферм ({city['name']})",
        "config": {
            "mapProvider": "openstreetmap",
            "latitude": city["additionalInfo"]["latitude"],
            "longitude": city["additionalInfo"]["longitude"],
            "zoomLevel": 10,
            "markers": []
        }
    }

    # Добавление маркеров для ферм
    for farm in farms:
        if farm["additionalInfo"]["latitude"] and farm["additionalInfo"]["longitude"]:
            farm_info = farm["additionalInfo"]
            marker = {
                "latitude": farm_info["latitude"],
                "longitude": farm_info["longitude"],
                "tooltip": f"Ферма: {farm['name']}",
                "actions": {
                    "onClick": {
                        "state": farm["name"],  # Переход в состояние фермы
                        "target": city["name"]  # Состояние города
                    }
                }
            }
            farm_map_widget["config"]["markers"].append(marker)

    # Добавление виджета карты ферм на состояние города
    city_state["configuration"]["widgets"]["farm_map"] = farm_map_widget
    city_state["configuration"]["layouts"]["main"]["widgets"].append({
        "id": "farm_map",
        "row": 0,
        "col": 0,
        "sizeX": 24,
        "sizeY": 12
    })

    # Добавление состояния города в дашборд
    dashboard["configuration"]["states"][city["name"]] = city_state

# Создание состояний для ферм
for farm in farms:
    farm_state = {
        "name": farm["name"],
        "root": False,
        "widgets": {},
        "layouts": {
            "main": {
                "widgets": [],
                "gridSettings": {
                    "backgroundColor": "#ffffff",
                    "columns": 24,
                    "margin": 10,
                    "backgroundSizeMode": "100%"
                }
            }
        }
    }

    # Добавление виджетов для фермы (например, данные датчиков)
    sensor_widget = {
        "type": "latest_values",
        "title": f"Данные фермы: {farm['name']}",
        "config": {
            "datasources": [
                {
                    "type": "entity",
                    "entityAlias": farm["name"],
                    "dataKeys": [
                        {"name": "humidity", "type": "numeric", "label": "Влажность"},
                        {"name": "temperature", "type": "numeric", "label": "Температура"}
                    ]
                }
            ]
        }
    }

    # Добавление виджета данных на состояние фермы
    farm_state["configuration"]["widgets"]["sensor_data"] = sensor_widget
    farm_state["configuration"]["layouts"]["main"]["widgets"].append({
        "id": "sensor_data",
        "row": 0,
        "col": 0,
        "sizeX": 24,
        "sizeY": 12
    })

    # Добавление состояния фермы в дашборд
    dashboard["configuration"]["states"][farm["name"]] = farm_state

# Сохранение дашборда
try:
    created_dashboard = rest_client.save_dashboard(body=dashboard)
    print(f"Дашборд создан: {created_dashboard['title']}")
except ApiException as e:
    print(f"Ошибка при создании дашборда: {e}")