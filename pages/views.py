from django.shortcuts import render
from django.db.models import Q
from django.views.generic import TemplateView, ListView



class HomepageTemplateView(TemplateView):
    template_name = "pages/index.html"


def get_object_or_404(request):
    return render(request, 'pages/404.html')
