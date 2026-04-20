import hashlib
import json
import time
from typing import Any

from django.core.cache import cache


SESSION_CACHE_KEY_PREFIX = 'orchestrator:session:'
SESSION_TTL = 1800


def build_user_binding_hash(context: dict[str, Any] | None) -> str:
    payload = {
        'kb_scope': _normalize_value((context or {}).get('kb_scope')),
        'project_id': (context or {}).get('project_id') or '',
        'role_code': (context or {}).get('role_code') or '',
        'source': (context or {}).get('source') or '',
        'user_id': (context or {}).get('user_id') or '',
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(serialized.encode('utf-8')).hexdigest()


def get_session_binding(session_id: str) -> dict[str, Any] | None:
    if not session_id:
        return None
    binding = cache.get(_cache_key(session_id))
    if isinstance(binding, dict):
        return binding
    return None


def set_session_binding(
    session_id: str,
    *,
    chat_id: str,
    application_id: str,
    api_key_id: str,
    user_binding_hash: str,
) -> dict[str, Any]:
    timestamp = time.time()
    binding = {
        'chat_id': chat_id,
        'application_id': application_id,
        'api_key_id': api_key_id,
        'user_binding_hash': user_binding_hash,
        'created_at': timestamp,
        'last_seen_at': timestamp,
    }
    cache.set(_cache_key(session_id), binding, timeout=SESSION_TTL)
    return binding


def touch_session_binding(session_id: str, binding: dict[str, Any]) -> dict[str, Any]:
    updated_binding = {
        **binding,
        'last_seen_at': time.time(),
    }
    cache.set(_cache_key(session_id), updated_binding, timeout=SESSION_TTL)
    return updated_binding


def get_session_cache_key(session_id: str) -> str:
    return _cache_key(session_id)


def _cache_key(session_id: str) -> str:
    return f'{SESSION_CACHE_KEY_PREFIX}{session_id}'


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        normalized_items = [_normalize_value(item) for item in value]
        return sorted(
            normalized_items,
            key=lambda item: json.dumps(item, sort_keys=True, separators=(',', ':'), ensure_ascii=False),
        )
    return value
