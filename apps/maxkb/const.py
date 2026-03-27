# -*- coding: utf-8 -*-
#
import os

from dotenv import load_dotenv

from .conf import ConfigManager

__all__ = ["BASE_DIR", "PROJECT_DIR", "VERSION", "CONFIG"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
VERSION = "2.0.0"

# load environment variables from .env file
load_dotenv(os.path.join(PROJECT_DIR, ".env"))
LOG_DIR = os.environ.get("MAXKB_LOG_DIR", os.path.join("/", "opt", "maxkb", "logs"))
# print(os.getenv('MAXKB_CONFIG'))
if os.getenv("MAXKB_CONFIG") is not None:
    config_root_path = PROJECT_DIR
else:
    config_root_path = os.path.abspath("/opt/maxkb/conf")

CONFIG = ConfigManager.load_user_config(root_path=config_root_path)
