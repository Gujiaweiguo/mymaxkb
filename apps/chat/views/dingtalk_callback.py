from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from chat.serializers.dingtalk_callback import DingtalkCallbackSerializer


@method_decorator(csrf_exempt, name="dispatch")
class DingtalkApplicationCallbackView(View):
    def post(self, request: HttpRequest, application_id: str):
        try:
            return DingtalkCallbackSerializer.receive_callback(
                application_id, request.GET, request.body
            )
        except ValueError as exc:
            return HttpResponse(str(exc), status=400, content_type="text/plain")
