from django.http import HttpResponse, HttpRequest, JsonResponse

# Create your views here.
def get_data(request: HttpRequest) -> HttpResponse:
    return JsonResponse({"status": "success", "data": "Hello, world!"})