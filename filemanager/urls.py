from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from . import views

from filemanager.views import (BrowserView, DetailView, UploadView, FolderList,
                               UploadFileView, DirectoryCreateView, FileShareView, RenameView, FileCreateView, SharedDocumentDetails,
                               DeleteView, ViewProfile, AllFiles, FilesGroup, FilesList, StarredFiles, SharedFiles, SharedOutgoing, SharedLinks, RecoverFiles, FileSettings, MailBox)

app_name= 'filemanager'

urlpatterns = [
    # re_path(r'^$', BrowserView.as_view(), name='browser'),
    re_path(r"^f/create/$", views.FolderCreate.as_view(), name="folder_create"),
    path('folder_list', FolderList.as_view(), name='folder_list'),
    re_path(r"^f/(?P<slug>[-\w]+)/$", views.FolderDetail.as_view(), name="folder_detail"),
    re_path(r"^f/upload_document/$", views.DocumentCreate.as_view(), name="document_create"),
    path('create/document/', views.create_document, name='create_document'),
    path('share/<int:id>/', views.share_file, name='share_file'),
    re_path(r"^f/(?P<pk>[-\w]+)/$", views.DocumentDetail.as_view(), name="document_detail"),
    path('shared-files/', views.shared_files, name='shared_files'),
    # path('shared-document-detail/<int:id>/', views.shared_document_detail, name='shared_document_detail'),
    path('shared-document-detail/<int:d_id>/<int:s_id>',  SharedDocumentDetails.as_view(), name='shared_document_details'),
    path('add-comment/<int:id>/', views.add_comment, name='add_comment'),
    path('browser/', BrowserView.as_view(), name='browser'),
    path('create/directory/', DirectoryCreateView.as_view(), name='create-directory'),
    path('create/', FileCreateView.as_view(), name='create_file'),
    
    # re_path(r"^f/(?P<slug>[-\w]+)/$", views.FolderDetail.as_view(), name="folder_detail"),
    # path('file-detail/<str:file_path>/', views.file_detail, name='file_detail'),
    
    re_path(r'^folder_detail/(?P<directory>.*)?$', views.folder_detail, name='folder_detail'),
    path('share/file/', FileShareView.as_view(), name='share-file'),
    re_path(r'^detail/$', DetailView.as_view(), name='detail'),
    re_path(r'^upload/$', UploadView.as_view(), name='upload'),
    re_path(r'^upload/file/$', csrf_exempt(UploadFileView.as_view()), name='upload-file'),
    re_path(r'^rename/$', RenameView.as_view(), name='rename'),
    re_path(r'^delete/$', DeleteView.as_view(), name='delete'),
  # re_path(r'^create/directory/$', DirectoryCreateView.as_view(), name='create-directory'),
    path('file-manager/', views.file_manager, name='file_manager'),
    re_path(r'^file-manager/(?P<directory>.*)?$', views.file_manager, name='file_manager'),
    # path('share/<str:file_path>/', views.share_file, name='share_file'),
    # path('add-comment/<str:file_path>/', views.add_comment, name='add_comment'),
    
    # path('download-file/<str:file_path>/', views.download_file, name='download_file'),
    path('download-file/<int:id>/', views.download, name='download'),
    path('download-iframe/<int:id>/', views.download_iframe, name='download_iframe'),
    # path('delete-file/<str:file_path>/', views.delete_file, name='delete_file'),
    path('delete-file/<int:id>/', views.delete_file, name='delete_file'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('save-info/<str:file_path>/', views.save_info, name='save_info'),
    

    path('download-file/<str:file_path>/', views.download_file, name='download_file'),
    path('view_profile/', ViewProfile.as_view(), name='view_profile'),
    path('files_all/', AllFiles.as_view(), name='files_all'),
    path('files_group/', FilesGroup.as_view(), name='files_group'),
    path('files_list/', FilesList.as_view(), name='files_list'),
    path('starred_files/', StarredFiles.as_view(), name='starred_files'),
    # path('shared_files/', SharedFiles.as_view(), name='shared_files'),
    path('shared_outgoing/', SharedOutgoing.as_view(), name='shared_outgoing'),
    path('shared_links/', SharedLinks.as_view(), name='shared_links'),
    path('recover_files/', RecoverFiles.as_view(), name='recover_files'),
    path('file_settings/', FileSettings.as_view(), name='file_settings'),
    path('mailbox/', MailBox.as_view(), name='mailbox'),



    
]


htmx_urlpatterns = [
    path('file-manager/', views.files_manager, name='files_manager'),
    # re_path(r'^file-manager/(?P<directory>.*)?/$', views.file_manager, name='file_manager'),
    
    
]

urlpatterns += htmx_urlpatterns