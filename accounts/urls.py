from django.urls import path
from . import views
from .views import (
    LoginTemplateView, SignUpView,  
)

app_name = 'accounts'

urlpatterns = [
    path('create_portal_account/', SignUpView.as_view(), name='create_portal_account'),
    path('signin', LoginTemplateView.as_view(), name='signin'),
    path('login', views.login, name='login'), 
    path('logout', views.logout, name='logout'),
    

    
    
    ]