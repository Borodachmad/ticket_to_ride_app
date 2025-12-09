
import cv2
import numpy as np
import json

# Загружаем изображение карты
img = cv2.imread("/home/boroda/project/1/ticket_to_ride_ai/assets/map.jpeg")
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Предварительно определяем цвета маршрутов в HSV (пример)
colors_hsv = {
    "red": ([0, 70, 50], [10, 255, 255]),
    "yellow": ([20, 100, 100], [30, 255, 255]),
    "blue": ([100, 150, 0], [130, 255, 255]),
    "green": ([50, 70, 50], [70, 255, 255]),
    "black": ([0, 0, 0], [180, 255, 50]),
    "orange": ([10, 100, 100], [20, 255, 255]),
    "pink": ([140, 50, 50], [170, 255, 255]),
    "white": ([0, 0, 200], [180, 20, 255]),
    "grey": ([0, 0, 50], [180, 30, 200])
}

routes = []

for color, (lower, upper) in colors_hsv.items():
    lower = np.array(lower)
    upper = np.array(upper)
    mask = cv2.inRange(img_hsv, lower, upper)
    
    # Находим контуры сегментов
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) < 50:  # фильтруем слишком маленькие объекты
            continue
        coords = cnt.reshape(-1, 2).tolist()
        routes.append({
            "id": f"{color}_{len(routes)}",
            "color": color,
            "coords": coords,
            "length": len(coords)
        })

# Сохраняем JSON
with open("routes.json", "w") as f:
    json.dump({"routes": routes}, f, indent=4)
