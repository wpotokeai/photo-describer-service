import json

import click
from dotenv import load_dotenv

from describer import generate_description
from formatter import format_for_display, format_for_export

load_dotenv()


@click.command(context_settings={"help_option_names": ["--help"]})
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--hint", "-h", default="", help="Подсказка о содержимом фото")
@click.option("--json-out", "-j", is_flag=True, help="Вывести результат в JSON")
@click.option(
    "--export",
    "-e",
    type=click.Path(),
    default=None,
    help="Сохранить описание в JSON-файл",
)
def main(image_path, hint, json_out, export):
    """Генерирует описание для фотографии с помощью Claude API."""
    click.echo(f"⏳ Анализирую изображение: {image_path}")

    result = generate_description(image_path, user_hint=hint)

    if json_out:
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        click.echo(format_for_display(result))

    if export:
        export_data = format_for_export(result)
        with open(export, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        click.echo(f"\n✅ Описание сохранено в: {export}")


if __name__ == "__main__":
    main()
