from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.permission_constants import (
    Auth,
    PermissionConstants,
    RoleConstants,
)
from common.exception.app_exception import AppAuthenticationFailed
from system_manage.models import SystemApiKey


class SystemApiKeyAuth(AuthBaseHandle):
    def support(self, request, token: str, get_token_details):
        return str(token).startswith("system-")

    def handle(self, request, token: str, get_token_details):
        system_api_key = QuerySet(SystemApiKey).filter(secret_key=token).first()
        if system_api_key is None or not system_api_key.is_active:
            raise AppAuthenticationFailed(500, _("Secret key is invalid"))
        if (
            system_api_key.is_permanent is False
            and system_api_key.expire_time < timezone.now()
        ):
            raise AppAuthenticationFailed(500, _("Secret key is expired"))
        return None, Auth(
            current_role_list=[RoleConstants.ADMIN.value.__str__()],
            permission_list=[PermissionConstants.SYSTEM_API_KEY_EDIT],
        )
