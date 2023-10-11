from django.urls import path
from . import views
from .views import (
    DashboardView,
    RecoverFiles,
    FileSettings,
    SharedOutgoing,
    UserCreateView,

    
    

   
)


app_name = 'sys_admin'

urlpatterns = [
	path('', DashboardView.as_view(), name='sys_admin_dashboard'),
    path('shared-files/', views.shared_files, name='shared_files'),
    path('recover_files/', RecoverFiles.as_view(), name='recover_files'),
    path('file_settings/', FileSettings.as_view(), name='file_settings'),
    path('shared_outgoing/', SharedOutgoing.as_view(), name='shared_outgoing'),
    path('create_user',  UserCreateView.as_view(), name='create_user'),

        
    ]