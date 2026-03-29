def format_for_display(data: dict) -> str:
    """Отформатировать результат для вывода в терминал."""
    if "raw" in data:
        return f"[Сырой ответ]\n{data['raw']}"

    lines = [
        f"📌 ЗАГОЛОВОК:\n  {data.get('title', '—')}",
        f"\n📝 КРАТКОЕ ОПИСАНИЕ:\n  {data.get('short_description', '—')}",
        f"\n📄 ПОЛНОЕ ОПИСАНИЕ:\n  {data.get('full_description', '—')}",
        f"\n🏷️  ТЕГИ:\n  {data.get('tags', '—')}",
        f"\n📂 КАТЕГОРИЯ:\n  {data.get('category', '—')}",
    ]

    usage = data.get("_usage", {})
    if usage:
        cost_input = usage["input_tokens"] * 0.000001
        cost_output = usage["output_tokens"] * 0.000005
        lines.append(
            f"\n💰 ТОКЕНЫ: вход={usage['input_tokens']}, "
            f"выход={usage['output_tokens']} "
            f"(~${cost_input + cost_output:.6f})"
        )

    return "\n".join(lines)


def format_for_export(data: dict) -> dict:
    """Вернуть чистый словарь для выгрузки на платформу (без служебных полей)."""
    export_keys = ["title", "short_description", "full_description", "tags", "category"]
    return {k: data[k] for k in export_keys if k in data}
