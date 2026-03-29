import anthropic
import base64
import json
from pathlib import Path

from config import MODEL_ID, MAX_TOKENS, PLATFORM_PROMPT, MAX_IMAGE_SIZE_MB

client = anthropic.Anthropic()  # читает ANTHROPIC_API_KEY из окружения

MEDIA_TYPE_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def _validate_size_mb(data: bytes) -> None:
    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(f"Файл слишком большой: {size_mb:.1f} MB (макс. {MAX_IMAGE_SIZE_MB} MB)")


def _media_type_for_suffix(suffix: str) -> str:
    suf = suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
    media_type = MEDIA_TYPE_MAP.get(suf)
    if not media_type:
        raise ValueError(f"Неподдерживаемый формат: {suffix}")
    return media_type


def _call_claude(image_data_b64: str, media_type: str, user_hint: str = "") -> dict:
    user_content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data_b64,
            },
        }
    ]
    prompt_text = "Опиши это изображение для платформы."
    if user_hint:
        prompt_text += f" Подсказка: {user_hint}"
    user_content.append({"type": "text", "text": prompt_text})

    message = client.messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=PLATFORM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw_text = message.content[0].text

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {"raw": raw_text}

    result["_usage"] = {
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens,
    }
    return result


def load_image(image_path: str) -> tuple[str, str]:
    """Загрузить изображение и вернуть (base64_data, media_type)."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {image_path}")

    raw = path.read_bytes()
    _validate_size_mb(raw)
    media_type = _media_type_for_suffix(path.suffix.lower())
    image_data = base64.standard_b64encode(raw).decode("utf-8")

    return image_data, media_type


def generate_description(image_path: str, user_hint: str = "") -> dict:
    """
    Отправить изображение в Claude и получить структурированное описание.

    Args:
        image_path: Путь к файлу изображения
        user_hint: Необязательная подсказка (например, 'это товар для кухни')

    Returns:
        dict с полями: title, short_description, full_description, tags, category
    """
    image_data, media_type = load_image(image_path)
    return _call_claude(image_data, media_type, user_hint)


def generate_description_from_bytes(
    data: bytes,
    filename: str,
    user_hint: str = "",
) -> dict:
    """
    То же, что generate_description, но из байтов загруженного файла.
    `filename` нужен для определения расширения (.jpg и т.д.).
    """
    _validate_size_mb(data)
    suffix = Path(filename).suffix.lower() or ".jpg"
    media_type = _media_type_for_suffix(suffix)
    image_data = base64.standard_b64encode(data).decode("utf-8")
    return _call_claude(image_data, media_type, user_hint)
