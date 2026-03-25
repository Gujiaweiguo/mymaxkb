from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from system_manage.serializers.appearance_setting import (
    AppearanceSettingResponseSerializer,
)


class AppearanceSettingResult(ResultSerializer):
    def get_data(self):
        return AppearanceSettingResponseSerializer()


class AppearanceSettingAPI(APIMixin):
    @staticmethod
    def get_response():
        return AppearanceSettingResult
