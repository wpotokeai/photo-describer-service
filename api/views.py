from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from describer import generate_description_from_bytes


@csrf_exempt
@require_http_methods(["POST"])
def describe(request):
    """
    multipart/form-data: поле `file` — изображение, опционально `hint` — текст.
    """
    if "file" not in request.FILES:
        return JsonResponse({"error": "Нет файла в поле file"}, status=400)

    uploaded = request.FILES["file"]
    hint = (request.POST.get("hint") or "").strip()
    data = uploaded.read()

    try:
        result = generate_description_from_bytes(data, uploaded.name, user_hint=hint)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(result, json_dumps_params={"ensure_ascii": False})
