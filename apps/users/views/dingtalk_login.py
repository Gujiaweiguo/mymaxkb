from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from users.serializers.dingtalk_login import DingtalkLoginSerializer


class DingtalkLoginView(APIView):
    @extend_schema(
        methods=["GET"],
        summary=_("DingTalk log in"),
        description=_("DingTalk log in"),
        operation_id="dingtalk_login",
        parameters=[
            OpenApiParameter(
                name="code",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            )
        ],
        responses=None,
        tags=["User Management"],
    )
    def get(self, request: Request):
        return result.success(
            DingtalkLoginSerializer(
                data={"code": request.query_params.get("code")}
            ).login()
        )
