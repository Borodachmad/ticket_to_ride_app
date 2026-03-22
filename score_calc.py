from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np


# Очки за маршруты по длине (правила Ticket to Ride)
ROUTE_SCORES = {
    1: 1,
    2: 2,
    3: 4,
    4: 7,
    5: 10,
    6: 15,
}

# Цвета игроков в HSV — повышенная насыщенность, чтобы ловить пластик, а не печать
# Пластиковые вагончики ярче и насыщеннее напечатанных маршрутов на доске
PLAYER_COLORS_HSV = {
    "red": [
        ([0, 120, 80], [8, 255, 255]),     # красный нижний диапазон
        ([170, 120, 80], [180, 255, 255]),  # красный верхний диапазон (Hue wraparound)
    ],
    "yellow": [
        ([20, 130, 120], [35, 255, 255]),
    ],
    "blue": [
        ([100, 150, 70], [125, 255, 255]),
    ],
    "green": [
        ([55, 100, 70], [80, 255, 255]),
    ],
    "black": [
        ([0, 0, 0], [180, 80, 45]),
    ],
}

# Максимальное кол-во вагонов в одном маршруте
MAX_ROUTE_LENGTH = 6

# Максимальная сторона изображения для анализа.
# Исходный файл может быть больше, но детекция работает на уменьшенной копии.
MAX_ANALYSIS_DIMENSION = 2000

# Параметры для построения маски и слотов перегонов из routes.json
ROUTE_MIN_ASPECT = 2.5
ROUTE_MIN_AREA = 8
ROUTE_MAX_AREA = 2500
MIN_MATCH_COUNT = 20
SLOT_CHANGED_RATIO = 0.18
SLOT_COLOR_RATIO = 0.10


def _contour_center(contour):
    """Возвращает центр контура (cx, cy)."""
    m = cv2.moments(contour)
    if m["m00"] == 0:
        x, y, w, h = cv2.boundingRect(contour)
        return (x + w // 2, y + h // 2)
    return (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"]))


def _resize_for_analysis(image):
    """Уменьшает изображение до безопасного размера для анализа."""
    height, width = image.shape[:2]
    longest_side = max(width, height)
    if longest_side <= MAX_ANALYSIS_DIMENSION:
        return image, 1.0

    scale = MAX_ANALYSIS_DIMENSION / float(longest_side)
    resized = cv2.resize(
        image,
        (int(width * scale), int(height * scale)),
        interpolation=cv2.INTER_AREA,
    )
    return resized, scale


@lru_cache(maxsize=1)
def _load_reference_board():
    """Загружает эталонную пустую карту из assets/map.jpeg."""
    reference_path = Path(__file__).with_name("assets").joinpath("map.jpeg")
    image = cv2.imread(str(reference_path))
    if image is None:
        raise FileNotFoundError(f"Не удалось загрузить эталонную карту: {reference_path}")
    return image


def _align_to_reference(image, reference_image):
    """Выравнивает входное фото относительно эталонной карты.

    Если гомография не найдена, возвращает просто уменьшенную копию входа.
    """
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    reference_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

    detector = cv2.ORB_create(3000)
    image_keypoints, image_descriptors = detector.detectAndCompute(image_gray, None)
    reference_keypoints, reference_descriptors = detector.detectAndCompute(reference_gray, None)

    if image_descriptors is None or reference_descriptors is None:
        return image, False

    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(image_descriptors, reference_descriptors)
    if len(matches) < MIN_MATCH_COUNT:
        return image, False

    matches = sorted(matches, key=lambda match: match.distance)[:250]
    source_points = np.float32([image_keypoints[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    destination_points = np.float32([reference_keypoints[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    homography, mask = cv2.findHomography(source_points, destination_points, cv2.RANSAC, 5.0)
    if homography is None or mask is None or int(mask.sum()) < MIN_MATCH_COUNT:
        return image, False

    aligned = cv2.warpPerspective(
        image,
        homography,
        (reference_image.shape[1], reference_image.shape[0]),
        flags=cv2.INTER_LINEAR,
    )
    return aligned, True


def _build_difference_mask(image, reference_image):
    """Оставляет только то, что отличается от пустой карты."""
    difference = cv2.absdiff(image, reference_image)
    difference_gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(difference_gray, 28, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


@lru_cache(maxsize=8)
def _build_route_slots(width, height):
    """Строит список возможных слотов перегонов из routes.json."""
    routes_path = Path(__file__).with_name("routes.json")

    if not routes_path.exists():
        return []

    try:
        import json

        with routes_path.open("r", encoding="utf-8") as file:
            routes = json.load(file).get("routes", [])
    except Exception:
        return []

    slots = []
    source_width = 9331.0
    source_height = 6208.0
    scale_x = width / source_width
    scale_y = height / source_height

    for route in routes:
        coords = np.array(route.get("coords", []), dtype=np.float32)
        if len(coords) < 5:
            continue

        coords[:, 0] *= scale_x
        coords[:, 1] *= scale_y
        contour = coords.astype(np.int32)

        area = cv2.contourArea(contour)
        rect = cv2.minAreaRect(contour)
        rect_width, rect_height = rect[1]
        if rect_width == 0 or rect_height == 0:
            continue

        aspect_ratio = max(rect_width, rect_height) / max(1.0, min(rect_width, rect_height))
        if ROUTE_MIN_AREA <= area <= ROUTE_MAX_AREA and aspect_ratio >= ROUTE_MIN_ASPECT:
            slots.append(
                {
                    "contour": contour,
                    "center": _contour_center(contour),
                    "area": area,
                    "printed_color": route.get("color", "unknown"),
                }
            )

    return slots


def _build_route_zone_mask(width, height):
    """Строит маску зон, где на поле могут лежать вагончики."""
    slots = _build_route_slots(width, height)
    if not slots:
        return np.full((height, width), 255, dtype=np.uint8)

    route_mask = np.zeros((height, width), dtype=np.uint8)
    for slot in slots:
        cv2.drawContours(route_mask, [slot["contour"]], -1, 255, cv2.FILLED)

    dilation = max(9, int(max(width, height) * 0.007))
    if dilation % 2 == 0:
        dilation += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation, dilation))
    return cv2.dilate(route_mask, kernel)


def _detect_occupied_slots(image_hsv, difference_mask, route_slots):
    """Определяет, какие слоты перегонов заняты, и какого они цвета."""
    occupied = []

    for slot in route_slots:
        x, y, width, height = cv2.boundingRect(slot["contour"])
        if width <= 0 or height <= 0:
            continue

        contour_in_box = slot["contour"].copy()
        contour_in_box[:, 0] -= x
        contour_in_box[:, 1] -= y

        slot_mask = np.zeros((height, width), dtype=np.uint8)
        cv2.drawContours(slot_mask, [contour_in_box], -1, 255, cv2.FILLED)

        diff_crop = difference_mask[y : y + height, x : x + width]
        changed = cv2.bitwise_and(diff_crop, slot_mask)
        slot_pixels = int(np.count_nonzero(slot_mask))
        if slot_pixels == 0:
            continue

        changed_ratio = np.count_nonzero(changed) / float(slot_pixels)
        if changed_ratio < SLOT_CHANGED_RATIO:
            continue

        hsv_crop = image_hsv[y : y + height, x : x + width]
        color_scores = {}
        for color, hsv_ranges in PLAYER_COLORS_HSV.items():
            color_mask = np.zeros((height, width), dtype=np.uint8)
            for lower, upper in hsv_ranges:
                mask = cv2.inRange(hsv_crop, np.array(lower), np.array(upper))
                color_mask = cv2.bitwise_or(color_mask, mask)

            color_mask = cv2.bitwise_and(color_mask, changed)
            color_scores[color] = np.count_nonzero(color_mask)

        dominant_color, dominant_pixels = max(color_scores.items(), key=lambda item: item[1])
        color_ratio = dominant_pixels / float(slot_pixels)
        if color_ratio < SLOT_COLOR_RATIO:
            continue

        occupied.append(
            {
                "color": dominant_color,
                "center": slot["center"],
                "changed_ratio": changed_ratio,
                "color_ratio": color_ratio,
                "printed_color": slot["printed_color"],
            }
        )

    return occupied


def _is_wagon_shape(contour, median_area, area_tolerance=3.0):
    """Проверяет, похож ли контур на вагончик по форме.
    
    Критерии:
    - Solidity >= 0.5 (достаточно компактная фигура)
    - Aspect ratio 1:1 .. 5:1 (вагончик вытянутый, но не слишком)
    - Площадь не сильно отличается от медианной (одинаковые детали)
    """
    area = cv2.contourArea(contour)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    if hull_area == 0:
        return False
    solidity = area / hull_area
    if solidity < 0.65:
        return False

    # Aspect ratio через minAreaRect
    rect = cv2.minAreaRect(contour)
    w, h = rect[1]
    if w == 0 or h == 0:
        return False
    aspect = max(w, h) / min(w, h)
    if aspect < 1.2 or aspect > 4.5:
        return False

    # Проверка, что площадь не слишком далека от медианы
    if median_area > 0:
        ratio = area / median_area
        if ratio < 1.0 / area_tolerance or ratio > area_tolerance:
            return False

    return True


def _filter_wagons(contours, img_area):
    """Фильтрует контуры, оставляя только похожие на вагончики.
    
    Этапы:
    1. Отсеиваем слишком мелкие и слишком крупные по площади
    2. Вычисляем медианную площадь оставшихся
    3. Фильтруем по форме (solidity, aspect ratio, близость к медиане)
    """
    if not contours:
        return []

    # Адаптивные пороги на основе размера изображения
    # Вагончик занимает примерно 0.001% — 0.05% площади фото
    min_area = img_area * 0.000003
    max_area = img_area * 0.0006

    # Первый проход: грубая фильтрация по площади
    candidates = []
    for c in contours:
        a = cv2.contourArea(c)
        if min_area <= a <= max_area:
            candidates.append(c)

    if not candidates:
        return []

    # Медианная площадь — ориентир размера вагончика
    areas = [cv2.contourArea(c) for c in candidates]
    median_area = float(np.median(areas))

    # Второй проход: фильтрация по форме
    wagons = [c for c in candidates if _is_wagon_shape(c, median_area)]

    return wagons


def _cluster_contours(contours, max_dist):
    """Группирует контуры в кластеры (маршруты) по расстоянию."""
    if not contours:
        return []

    centers = [_contour_center(c) for c in contours]
    clusters = []

    for i, center in enumerate(centers):
        best_cluster = None
        best_dist = float("inf")
        for cluster in clusters:
            cx = np.mean([centers[j][0] for j in cluster])
            cy = np.mean([centers[j][1] for j in cluster])
            dist = np.sqrt((center[0] - cx) ** 2 + (center[1] - cy) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_cluster = cluster
        if best_cluster is not None and best_dist <= max_dist:
            best_cluster.append(i)
        else:
            clusters.append([i])

    return clusters


def detect_routes(image_path: str) -> dict:
    """Детектирует вагончики игроков на фото и считает очки."""
    original_image = cv2.imread(image_path)
    if original_image is None:
        return {"success": False, "error": "Не удалось загрузить изображение"}

    original_height, original_width = original_image.shape[:2]
    reference_original = _load_reference_board()
    reference_image, _ = _resize_for_analysis(reference_original)
    image = cv2.resize(
        original_image,
        (reference_image.shape[1], reference_image.shape[0]),
        interpolation=cv2.INTER_AREA,
    )
    image, aligned = _align_to_reference(image, reference_image)

    height, width = image.shape[:2]
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    route_slots = _build_route_slots(width, height)
    route_zone_mask = _build_route_zone_mask(width, height)
    difference_mask = _build_difference_mask(image, reference_image)

    # Адаптивный cluster_distance — пропорционален размеру изображения
    cluster_dist = max(18, int(width * 0.03))

    players = {}
    total_segments = 0

    difference_mask = cv2.bitwise_and(difference_mask, route_zone_mask)
    occupied_slots = _detect_occupied_slots(img_hsv, difference_mask, route_slots)

    occupied_by_color = {}
    for slot in occupied_slots:
        occupied_by_color.setdefault(slot["color"], []).append(slot)

    for color, color_slots in occupied_by_color.items():
        contours = []
        for slot in color_slots:
            center_x, center_y = slot["center"]
            contour = np.array([[[center_x, center_y]]], dtype=np.int32)
            contours.append(contour)

        clusters = _cluster_contours(contours, cluster_dist)

        routes = []
        score = 0
        segments = 0

        for cluster_indices in clusters:
            route_len = min(len(cluster_indices), MAX_ROUTE_LENGTH)
            route_score = ROUTE_SCORES.get(route_len, route_len * 2)
            score += route_score
            segments += len(cluster_indices)

            route_centers = [
                color_slots[i]["center"] for i in cluster_indices
            ]
            routes.append({
                "wagons": route_len,
                "score": route_score,
                "centers": route_centers,
            })

        total_segments += segments
        players[color] = {
            "segments": segments,
            "routes": routes,
            "routes_count": len(routes),
            "score": score,
        }

    return {
        "success": True,
        "players": players,
        "total_segments": total_segments,
        "width": original_width,
        "height": original_height,
        "analysis_width": width,
        "analysis_height": height,
        "aligned": aligned,
    }


def process_image(image_path: str) -> dict:
    """Основная функция обработки — вызывается из GUI."""
    return detect_routes(image_path)
