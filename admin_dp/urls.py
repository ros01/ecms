from django.urls import path
from . import views
from .views import (
    DashboardView,
    DashboardView2,
    FileView,
    ViewProfile,
    AllFiles,
    FilesGroup,
    FilesList,
    StarredFiles,
    # SharedFiles,
    SharedOutgoing,
    SharedLinks,
    RecoverFiles,
    FileSettings,
    IndexView,
    MailBox,
    DirectoryCreateView,
    BrowserView,
    

   
)


app_name = 'admin_dp'

urlpatterns = [
	path('', DashboardView.as_view(), name='admin_dashboard'),
    path('administration_dashboard/', DashboardView2.as_view(), name='administration_dashboard'),
	path('index/', IndexView.as_view(), name='index'),
	path('filemanager_dashboard/', FileView.as_view(), name='filemanager_dashboard'),
    path('view_profile/', ViewProfile.as_view(), name='view_profile'),
    path('files_all/', AllFiles.as_view(), name='files_all'),
    path('files_group/', FilesGroup.as_view(), name='files_group'),
    path('files_list/', FilesList.as_view(), name='files_list'),
    path('starred_files/', StarredFiles.as_view(), name='starred_files'),
    # path('shared_files/', SharedFiles.as_view(), name='shared_files'),
    path('shared-files/', views.shared_files, name='shared_files'),
    path('download-file/<str:file_path>/', views.download_file, name='download_file'),
    path('shared_outgoing/', SharedOutgoing.as_view(), name='shared_outgoing'),
    path('shared_links/', SharedLinks.as_view(), name='shared_links'),
    path('recover_files/', RecoverFiles.as_view(), name='recover_files'),
    path('file_settings/', FileSettings.as_view(), name='file_settings'),
    path('mailbox/', MailBox.as_view(), name='mailbox'),
    path('create/directory/', DirectoryCreateView.as_view(), name='create-directory'),
    path('directory_list', BrowserView.as_view(), name='browser'),
    # url(r'^create/directory/$', DirectoryCreateView.as_view(), name='create-directory'),



	



    
    ]