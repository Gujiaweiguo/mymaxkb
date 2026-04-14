# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： __init__.py.py
    @date：2025/11/5 15:14
    @desc:
"""
import logging

logger = logging.getLogger(__name__)

logger.info("runtime_profile=web")
from .web import *
