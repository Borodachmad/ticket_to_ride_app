import cv2


def process_image(image_path: str) -> dict:
    """Базовая обработка изображения. 
    Проверяет загрузку, конвертирует в HSV, возвращает метаданные.
    """

    # Загружаем фото
    img = cv2.imread(image_path)
    if img is None:
        return {"success": False, "error": "Не удалось загрузить изображение"}

    # Размер
    h, w = img.shape[:2]

    # Переводим в HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    return {
        "success": True,
        "width": w,
        "height": h,
        "info": "Изображение успешно обработано",
    }
