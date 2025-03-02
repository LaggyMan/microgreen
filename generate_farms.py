import requests
import csv
import random

# Функция для получения координат города
def get_city_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    return None, None

# Список городов
cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]

# Генерация данных
data = []
for city in cities:
    lat, lon = get_city_coordinates(city)
    if lat and lon:
        for i in range(1, 6): 
            farm_lat = lat + random.uniform(-0.1, 0.1) 
            farm_lon = lon + random.uniform(-0.1, 0.1)
            data.append({
                "city": city,
                "city_lat": lat,
                "city_lon": lon,
                "farm_name": f"Ферма {i} ({city})",
                "farm_lat": farm_lat,
                "farm_lon": farm_lon
            })

with open("cities_and_farms.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["city", "city_lat", "city_lon", "farm_name", "farm_lat", "farm_lon"])
    writer.writeheader()
    writer.writerows(data)

print("Данные сохранены в cities_and_farms.csv")