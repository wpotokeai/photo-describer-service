# Photo Description Generator

Python-приложение: принимает фотографию и генерирует структурированное описание для маркетплейса, фотостока или каталога через **Claude API** (модель `claude-haiku-4-5-20251001`).

## Требования

- Python 3.10+
- Ключ API Anthropic

## Установка

```bash
cd photo_describer
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

Скопируйте `.env` и укажите реальный ключ:

```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## Использование

```bash
python main.py photo.jpg
python main.py photo.jpg --hint "товар из кожи" --export result.json
python main.py photo.jpg --json-out
```

Справка:

```bash
python main.py --help
```

## Структура проекта

| Файл           | Назначение                         |
| -------------- | ---------------------------------- |
| `main.py`      | CLI                                |
| `describer.py` | Загрузка изображения, вызов Claude |
| `formatter.py` | Вывод в консоль и экспорт JSON     |
| `config.py`    | Модель, лимиты, системный промпт   |

## Оценка стоимости (ориентир)

По спецификации IntuitionLabs для Haiku 4.5: **$1 / MTok** вход, **$5 / MTok** выход. Типичный запрос: порядка **~$0.003** за одно фото (зависит от размера изображения и длины ответа).

## Расширения (идеи)

- Пакетная обработка папки (Batch API, скидка 50%)
- Разные промпты под Wildberries, Etsy, фотостоки
- Валидация ответа через Pydantic
- Retry (например, tenacity) и логирование
- Web: FastAPI + загрузка файла
```
