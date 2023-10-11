from django.urls import path
from . import views
from .views import (
    DashboardView,
    RecoverFiles,
    FileSettings,
    SharedOutgoing,
  

    
    

   
)


app_name = 'planning'

urlpatterns = [
	path('', DashboardView.as_view(), name='planning_dashboard'),
    path('shared-files/', views.shared_files, name='shared_files'),
    path('recover_files/', RecoverFiles.as_view(), name='recover_files'),
    path('file_settings/', FileSettings.as_view(), name='file_settings'),
    path('shared_outgoing/', SharedOutgoing.as_view(), name='shared_outgoing'),
    

        
    ]