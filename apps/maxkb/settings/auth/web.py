# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： auth.py
@date：2024/7/9 18:47
@desc:
"""

USER_TOKEN_AUTH = "common.auth.handle.impl.user_token.UserToken"
CHAT_ANONYMOUS_USER_AURH = (
    "common.auth.handle.impl.chat_anonymous_user_token.ChatAnonymousUserToken"
)
CHAT_USER_AUTH = "common.auth.handle.impl.chat_user_token.ChatUserTokenHandle"
APPLICATION_KEY_AUTH = "common.auth.handle.impl.application_key.ApplicationKey"
SYSTEM_API_KEY_AUTH = "common.auth.handle.impl.system_api_key.SystemApiKeyAuth"
AUTH_HANDLES = [USER_TOKEN_AUTH, SYSTEM_API_KEY_AUTH]

CHAT_AUTH_HANDLES = [CHAT_ANONYMOUS_USER_AURH, CHAT_USER_AUTH, APPLICATION_KEY_AUTH]
