from django.urls import path

from . import views

app_name = "models_provider"
# @formatter:off
urlpatterns = [
    path('provider', views.Provide.as_view()),
    path('provider/model_type_list', views.Provide.ModelTypeList.as_view()),
    path('provider/model_list', views.Provide.ModelList.as_view()),
    path('provider/model_params_form', views.Provide.ModelParamsForm.as_view()),
    path('provider/model_form', views.Provide.ModelForm.as_view()),
    path('workspace/<str:workspace_id>/model', views.ModelSetting.as_view()),
    path('workspace/<str:workspace_id>/model_list', views.ModelList.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>/model_params_form', views.ModelSetting.ModelParamsForm.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>', views.ModelSetting.Operate.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>/pause_download', views.ModelSetting.PauseDownload.as_view()),
    path('workspace/<str:workspace_id>/model/<str:model_id>/meta', views.ModelSetting.ModelMeta.as_view()),
    path('system/shared/workspace/<str:workspace_id>/model', views.WorkspaceSharedModelSetting.as_view()),
    path('system/shared/model', views.SystemSharedModelSetting.as_view()),
    path('system/resource/model/<int:current_page>/<int:page_size>', views.SystemResourceModelView.Page.as_view()),
    path('system/resource/model/<str:model_id>/meta', views.SystemResourceModelView.ModelMeta.as_view()),
    path('system/resource/model/<str:model_id>/pause_download', views.SystemResourceModelView.PauseDownload.as_view()),
    path('system/resource/model/<str:model_id>/model_params_form', views.SystemResourceModelView.ModelParamsForm.as_view()),
    path('system/resource/model/<str:model_id>', views.SystemResourceModelView.Operate.as_view()),
]
