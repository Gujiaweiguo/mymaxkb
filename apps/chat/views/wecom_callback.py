from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from chat.serializers.wecom_callback import WecomCallbackSerializer


@method_decorator(csrf_exempt, name="dispatch")
class WecomApplicationCallbackView(View):
    def get(self, request: HttpRequest, application_id: str):
        try:
            return WecomCallbackSerializer.verify_url(application_id, request.GET)
        except ValueError as exc:
            return HttpResponse(str(exc), status=400, content_type="text/plain")

    def post(self, request: HttpRequest, application_id: str):
        try:
            return WecomCallbackSerializer.receive_callback(
                application_id, request.GET, request.body
            )
        except ValueError as exc:
            return HttpResponse(str(exc), status=400, content_type="text/plain")
