from django.urls import path
from . import views
from .views import (
    HomepageTemplateView,
    



)

urlpatterns = [
    #path('', views.index, name='index'),
    path('', HomepageTemplateView.as_view(), name='index'),
    path('get_object_or_404', views.get_object_or_404, name='404'),
    
    
    ]