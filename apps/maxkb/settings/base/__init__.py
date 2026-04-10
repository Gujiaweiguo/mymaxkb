# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： __init__.py.py
    @date：2025/11/5 14:53
    @desc:
"""
import logging
import os

logger = logging.getLogger(__name__)

_server_name = os.environ.get('SERVER_NAME', 'web')
if _server_name == 'local_model':
    logger.info("runtime_profile=%s", _server_name)
    from .model import *
else:
    if 'SERVER_NAME' not in os.environ:
        logger.info("runtime_profile=web, fallback=true")
    else:
        logger.info("runtime_profile=%s", _server_name)
    from .web import *
