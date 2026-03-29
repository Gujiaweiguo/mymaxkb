# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： cross_domain_middleware.py
    @date：2024/5/8 13:36
    @desc:
"""
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from common.cache_data.application_api_key_cache import get_application_api_key
from system_manage.models import SystemApiKey


class CrossDomainMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.method == 'OPTIONS':
            return HttpResponse(status=200,
                                headers={
                                    "Access-Control-Allow-Origin": "*",
                                    "Access-Control-Allow-Methods": "GET,POST,DELETE,PUT",
                                    "Access-Control-Allow-Headers": "Origin,X-Requested-With,Content-Type,Accept,Authorization,token"})

    def process_response(self, request, response):
        auth = request.META.get('HTTP_AUTHORIZATION')
        origin = request.META.get('HTTP_ORIGIN')

        if auth is not None and origin is not None and any(
            [
                str(auth).startswith(prefix)
                for prefix in ['Bearer application-', 'Bearer agent-', 'Bearer system-']
            ]
        ):
            if str(auth).startswith('Bearer system-'):
                system_api_key = SystemApiKey.objects.filter(secret_key=str(auth)[7:]).first()
                api_key_data = {
                    'allow_cross_domain': system_api_key.allow_cross_domain if system_api_key is not None else False,
                    'cross_domain_list': system_api_key.cross_domain_list if system_api_key is not None else [],
                }
            else:
                api_key_data = get_application_api_key(str(auth), True)
            cross_domain_list = api_key_data.get('cross_domain_list', [])
            allow_cross_domain = api_key_data.get('allow_cross_domain', False)
            if allow_cross_domain:
                if cross_domain_list is None or len(cross_domain_list) == 0:
                    response['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PUT'
                    response[
                        'Access-Control-Allow-Headers'] = "Origin,X-Requested-With,Content-Type,Accept,Authorization,token"
                    response['Access-Control-Allow-Origin'] = "*"
                elif cross_domain_list.__contains__(origin):
                    response['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,PUT'
                    response[
                        'Access-Control-Allow-Headers'] = "Origin,X-Requested-With,Content-Type,Accept,Authorization,token"
                    response['Access-Control-Allow-Origin'] = origin
        return response
