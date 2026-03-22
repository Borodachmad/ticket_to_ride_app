import json

with open("routes.json", "r") as f:
    data = json.load(f)

compressed = []

for route in data["routes"]:
    coords = route["coords"]

    # берём только две ключевые точки: начало и конец
    start = coords[0]
    end = coords[-1]

    compressed.append({
        "id": route["id"],
        "color": route["color"],
        "length": route["length"],
        "coords": [start, end]
    })

with open("routes_small.json", "w") as f:
    json.dump(compressed, f, indent=2)

print("Готово! routes_small.json создан")
