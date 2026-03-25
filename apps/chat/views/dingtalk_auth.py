from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from chat.serializers.dingtalk_auth import DingtalkAuthenticationSerializer
from common.result import result


class DingtalkAuthentication(APIView):
    @extend_schema(
        methods=["GET"],
        description=_("DingTalk chat authentication"),
        summary=_("DingTalk chat authentication"),
        operation_id="dingtalk_chat_authentication",
        parameters=[
            OpenApiParameter(
                name="code",
                description=_("code"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
            OpenApiParameter(
                name="accessToken",
                description=_("accessToken"),
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
            ),
        ],
        responses=None,
        tags=["Chat"],
    )
    def get(self, request: Request):
        return result.success(
            {
                "token": DingtalkAuthenticationSerializer(
                    data={
                        "code": request.query_params.get("code"),
                        "access_token": request.query_params.get("accessToken"),
                    }
                ).auth()
            }
        )
