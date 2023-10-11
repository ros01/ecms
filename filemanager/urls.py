from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from . import views

from filemanager.views import (BrowserView, DetailView, UploadView, FolderList,
                               UploadFileView, DirectoryCreateView, FileShareView, RenameView,
                               DeleteView)

app_name= 'filemanager'

urlpatterns = [
    # re_path(r'^$', BrowserView.as_view(), name='browser'),
    path('browser/', BrowserView.as_view(), name='browser'),
    path('create/directory/', DirectoryCreateView.as_view(), name='create-directory'),
    re_path(r"^f/create/$", views.FolderCreate.as_view(), name="folder_create"),
    re_path(r"^f/(?P<pk>\d+)/$", views.FolderDetail.as_view(), name="folder_detail"),
    path('share/file/', FileShareView.as_view(), name='share-file'),
    re_path(r'^detail/$', DetailView.as_view(), name='detail'),
    re_path(r'^upload/$', UploadView.as_view(), name='upload'),
    re_path(r'^upload/file/$', csrf_exempt(UploadFileView.as_view()), name='upload-file'),
    re_path(r'^rename/$', RenameView.as_view(), name='rename'),
    re_path(r'^delete/$', DeleteView.as_view(), name='delete'),
  # re_path(r'^create/directory/$', DirectoryCreateView.as_view(), name='create-directory'),
    path('file-manager/', views.file_manager, name='file_manager'),
    re_path(r'^file-manager/(?P<directory>.*)?/$', views.file_manager, name='file_manager'),
    path('delete-file/<str:file_path>/', views.delete_file, name='delete_file'),
    path('share/<str:file_path>/', views.share_file, name='share_file'),
    path('add-comment/<str:file_path>/', views.add_comment, name='add_comment'),
    path('file-detail/<str:file_path>/', views.file_detail, name='file_detail'),
    path('download-file/<str:file_path>/', views.download_file, name='download_file'),
    path('upload-file/', views.upload_file, name='upload_file'),
    path('save-info/<str:file_path>/', views.save_info, name='save_info'),
    path('folder_list', FolderList.as_view(), name='folder_list'),

    
]


htmx_urlpatterns = [
    path('file-manager/', views.files_manager, name='files_manager'),
    # re_path(r'^file-manager/(?P<directory>.*)?/$', views.file_manager, name='file_manager'),
    
    
]

urlpatterns += htmx_urlpatterns