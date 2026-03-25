"""
@project: MaxKB-xpack-ee
@Author: niu
@file: shared_resource_auth.py
@date: 2026/3/11 11:22
@desc:
"""

from typing import List

from django.db.models import QuerySet

from common.database_model_manage.database_model_manage import DatabaseModelManage
from knowledge.models import Knowledge
from system_manage.models import (
    SharedAuthenticationType,
    SharedResourceAuthorization,
    SharedResourceType,
)
from tools.models import Tool


RESOURCE_TYPE_MAP = {
    "tool": SharedResourceType.TOOL,
    "knowledge": SharedResourceType.KNOWLEDGE,
}


def filter_ce_authorized_ids(
    resource_type: str, ids: List[str], workspace_id: str
) -> List[str]:
    shared_resource_type = RESOURCE_TYPE_MAP.get(resource_type)
    if shared_resource_type is None or not ids:
        return []

    authorization_map = {
        str(item.resource_id): item
        for item in QuerySet(SharedResourceAuthorization).filter(
            resource_type=shared_resource_type,
            resource_id__in=ids,
        )
    }

    authorized_ids = []
    for resource_id in ids:
        authorization = authorization_map.get(str(resource_id))
        if authorization is None:
            continue
        workspace_id_list = set(map(str, authorization.workspace_id_list or []))
        if authorization.authentication_type == SharedAuthenticationType.WHITE_LIST:
            if workspace_id in workspace_id_list:
                authorized_ids.append(resource_id)
            continue
        if workspace_id not in workspace_id_list:
            authorized_ids.append(resource_id)
    return authorized_ids


def filter_authorized_ids(
    resource_type: str, ids: List[str], workspace_id: str
) -> List[str]:
    """
    通用授权过滤函数

    @param resource_type: 资源类型 ('model', 'tool', 'knowledge')
    @param ids: 待过滤的ID列表
    @param workspace_id: 工作空间ID
    @return: 授权通过的ID列表
    """

    if not ids:
        return []

    auth_func = DatabaseModelManage.get_model(f"get_authorized_{resource_type}")

    model_class = {"tool": Tool, "knowledge": Knowledge}.get(resource_type)
    if model_class is None:
        return ids

    same_workspace_ids = list(
        QuerySet(model_class)
        .filter(id__in=ids, workspace_id=workspace_id)
        .values_list("id", flat=True)
    )

    cross_workspace_ids = [i for i in ids if i not in set(map(str, same_workspace_ids))]

    authorized_ids = set(map(str, same_workspace_ids))

    if cross_workspace_ids and auth_func is not None:
        cross_queryset = QuerySet(model_class).filter(id__in=cross_workspace_ids)
        authorized = auth_func(cross_queryset, workspace_id)
        authorized_ids.update(str(r.id) for r in authorized)
    elif cross_workspace_ids:
        authorized_ids.update(
            map(
                str,
                filter_ce_authorized_ids(
                    resource_type, cross_workspace_ids, workspace_id
                ),
            )
        )

    return [i for i in ids if i in authorized_ids]
