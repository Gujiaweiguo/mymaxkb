from django.urls import path

from . import views

app_name = "system_manage"
# @formatter:off
urlpatterns = [
    path("workspace", views.WorkspaceManageView.as_view()),
    path("workspace/<str:workspace_id>", views.WorkspaceManageOperateView.as_view()),
    path(
        "workspace/<str:workspace_id>/check",
        views.WorkspaceManageDeleteCheckView.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/user_list/<int:current_page>/<int:page_size>",
        views.WorkspaceMemberPageView.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/add_member",
        views.WorkspaceMemberCreateView.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/remove_member/<str:user_relation_id>",
        views.WorkspaceMemberDeleteView.as_view(),
    ),
    path("role_list/current_user", views.WorkspaceRoleListView.as_view()),
    path("system/chat_user/list", views.ChatUserListView.as_view()),
    path("system/chat_user", views.ChatUserManageView.as_view()),
    path(
        "system/chat_user/user_manage/<int:current_page>/<int:page_size>",
        views.ChatUserPageView.as_view(),
    ),
    path("system/chat_user/batch_add_group", views.ChatUserBatchAddGroupView.as_view()),
    path("system/chat_user/batch_delete", views.ChatUserBatchDeleteView.as_view()),
    path("system/chat_user/sync_types", views.ChatUserSyncTypeView.as_view()),
    path("system/chat_user/sync/<str:sync_type>", views.ChatUserSyncView.as_view()),
    path(
        "system/chat_user/<str:user_id>/re_password",
        views.ChatUserPasswordView.as_view(),
    ),
    path("system/chat_user/<str:user_id>", views.ChatUserOperateView.as_view()),
    path("system/api_key", views.SystemApiKeyView.as_view()),
    path(
        "system/api_key/<int:current_page>/<int:page_size>",
        views.SystemApiKeyView.Page.as_view(),
    ),
    path("system/api_key/<str:api_key_id>", views.SystemApiKeyView.Operate.as_view()),
    path("system/group", views.UserGroupView.as_view()),
    path("system/group/<str:user_group_id>", views.UserGroupDeleteView.as_view()),
    path(
        "system/group/<str:user_group_id>/add_member",
        views.UserGroupMemberAddView.as_view(),
    ),
    path(
        "system/group/<str:user_group_id>/remove_member",
        views.UserGroupMemberRemoveView.as_view(),
    ),
    path(
        "system/group/<str:user_group_id>/user_list/<int:current_page>/<int:page_size>",
        views.UserGroupMemberPageView.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>/resource/<str:resource>",
        views.WorkSpaceUserResourcePermissionView.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/user_resource_permission/user/<str:user_id>/resource/<str:resource>/<int:current_page>/<int:page_size>",
        views.WorkSpaceUserResourcePermissionView.Page.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/resource_user_permission/resource/<str:target>/resource/<str:resource>",
        views.WorkspaceResourceUserPermissionView.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/resource_user_permission/resource/<str:target>/resource/<str:resource>/<int:current_page>/<int:page_size>",
        views.WorkspaceResourceUserPermissionView.Page.as_view(),
    ),
    path(
        "workspace/<str:workspace_id>/resource_mapping/<str:resource>/<str:resource_id>/<int:current_page>/<int:page_size>",
        views.ResourceMappingView.as_view(),
    ),
    path("email_setting", views.SystemSetting.Email.as_view()),
    path("display/info", views.AppearanceSettingView.as_view()),
    path("display/update", views.AppearanceSettingOperateView.as_view()),
    path("platform/source", views.PlatformSourceView.as_view()),
    path("chat_user/auth/platform/source", views.ChatUserPlatformSourceView.as_view()),
    path("auth/setting", views.LoginAuthSettingView.as_view()),
    path("login/auth/setting", views.PublicLoginAuthSettingView.as_view()),
    path(
        "system/shared/<str:resource_type>/<str:resource_id>/authorization",
        views.SharedResourceAuthorizationView.as_view(),
    ),
    path("profile", views.SystemProfile.as_view()),
    path("system/profile", views.SystemProfileApiKey.as_view()),
    path(
        "operate_log/<int:current_page>/<int:page_size>",
        views.OperateLogPageView.as_view(),
    ),
    path(
        "operate_log/menu_operation_option/", views.OperateLogMenuOptionView.as_view()
    ),
    path("operate_log/export/", views.OperateLogExportView.as_view()),
    path("operate_log/get_clean_time", views.OperateLogCleanTimeView.as_view()),
    path("operate_log/save", views.OperateLogCleanTimeView.as_view()),
    path("valid/<str:valid_type>/<int:valid_count>", views.Valid.as_view()),
]
