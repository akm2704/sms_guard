"""Task 2: health endpoint. ML API will be built in task 14."""
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})
