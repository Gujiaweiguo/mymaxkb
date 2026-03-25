from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from chat.serializers.wecom_auth import WecomAuthenticationSerializer
from common.result import result


class WecomAuthentication(APIView):
    @extend_schema(
        methods=["GET"],
        description=_("WeCom chat authentication"),
        summary=_("WeCom chat authentication"),
        operation_id="wecom_chat_authentication",
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
                "token": WecomAuthenticationSerializer(
                    data={
                        "code": request.query_params.get("code"),
                        "access_token": request.query_params.get("accessToken"),
                    }
                ).auth()
            }
        )
