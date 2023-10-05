from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import F
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views import static
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
    FormView, 
    ListView,
)
from django.views.generic.detail import (
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
)
from django.views.generic.edit import FormMixin, ProcessFormView

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
# from .forms import (
#     ColleagueFolderShareForm,
#     DocumentCreateForm,
#     DocumentCreateFormWithName,
#     FolderCreateForm,
# )
# from .hooks import hookset
# from .models import Document, Folder, UserStorage
from django.contrib.auth import get_user_model
User = get_user_model()

from filemanager.forms import DirectoryCreateForm, RenameForm
from filemanager.core import Filemanager
import re

import json

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.shortcuts import HttpResponse
from django.shortcuts import reverse
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin


# Create your views here.

class IndexView(LoginRequiredMixin, TemplateView):

    template_name = "admin_dp/index.html"

    def get_context_data(self, **kwargs):
        ctx = kwargs
        ctx.update({
            "members": Folder.objects.members(None, user=self.request.user),
            "storage": self.request.user.storage,
            "can_share": False,
        })
        return ctx


class DashboardView2(TemplateView):
    template_name = "admin_dp/admin_dashboard.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(DashboardView2, self).get_context_data(*args, **kwargs)
        return context


class DashboardView(TemplateView):
    #template_name = "administration/admin_dept_dashboard_main.html"
    template_name = "admin_dp/admin_dp_dashboard.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(DashboardView, self).get_context_data(*args, **kwargs)
        return context


class FileView(TemplateView):
    template_name = "admin_dp/admin_filemanager.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(FileView, self).get_context_data(*args, **kwargs)
        return context

class ViewProfile(TemplateView):
    template_name = "admin_dp/viewprofile.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(ViewProfile, self).get_context_data(*args, **kwargs)
        return context

class AllFiles(TemplateView):
    template_name = "admin_dp/admin_files.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(AllFiles, self).get_context_data(*args, **kwargs)
        return context

class FilesGroup(TemplateView):
    template_name = "admin_dp/files_group_view.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(FilesGroup, self).get_context_data(*args, **kwargs)
        return context

class FilesList(TemplateView):
    template_name = "admin_dp/files_list_view.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(FilesList, self).get_context_data(*args, **kwargs)
        return context
       
class StarredFiles(TemplateView):
    template_name = "admin_dp/starred_files.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(StarredFiles, self).get_context_data(*args, **kwargs)
        return context


class SharedFiles(TemplateView):
    template_name = "admin_dp/shared_files.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(SharedFiles, self).get_context_data(*args, **kwargs)
        return context



class SharedOutgoing(TemplateView):
    template_name = "admin_dp/shared_outgoing.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(SharedOutgoing, self).get_context_data(*args, **kwargs)


class SharedLinks(TemplateView):
    template_name = "admin_dp/shared_links.html"

    def get_context_data(self, *args, **kwargs):
        context = super(SharedLinks, self).get_context_data(*args, **kwargs)

class RecoverFiles(TemplateView):
    template_name = "admin_dp/recovery.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RecoverFiles, self).get_context_data(*args, **kwargs)



class FileSettings(TemplateView):
    template_name = "admin_dp/setting.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FileSettings, self).get_context_data(*args, **kwargs)



class MailBox(TemplateView):
    template_name = "admin_dp/mailbox.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MailBox, self).get_context_data(*args, **kwargs)

class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type']='application/javascript; charset=utf8'
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context





class FilemanagerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        params = dict(request.GET)
        params.update(dict(request.POST))

        self.fm = Filemanager()
        if 'path' in params and len(params['path'][0]) > 0:
            self.fm.update_path(params['path'][0])
        if 'popup' in params:
            self.popup = params['popup']

        return super(FilemanagerMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(FilemanagerMixin, self).get_context_data(*args, **kwargs)

        self.fm.patch_context_data(context)

        if hasattr(self, 'popup'):
            context['popup'] = self.popup

        if hasattr(self, 'extra_breadcrumbs') and isinstance(self.extra_breadcrumbs, list):
            context['breadcrumbs'] += self.extra_breadcrumbs

        return context


class BrowserView(FilemanagerMixin, TemplateView):
    template_name = 'filemanager/browser/filemanager_list.html'

    def dispatch(self, request, *args, **kwargs):
        self.popup = self.request.GET.get('popup', 0) == '1'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['popup'] = self.popup

        query = self.request.GET.get('q')
        search_params = self.request.GET.get('search_param')

        if query:
            if(re.match('here', search_params, re.I)):
                files = self.fm.directory_list()

                q = []
                for file in files:
                    if re.search(query, file['filename'], re.I):
                        q.append(file)
                    try:
                        if file['filetype'] == 'File':
                            with open('media/uploads/'+file['filepath']) as f:
                                content = f.read()
                                if query in content:
                                    q.append(file)
                    except:
                        pass

                context['files'] = q
                context['empty'] = 'No item found'

            else:
                context['files'] = self.fm.search(query)
                context['empty'] = 'No item found'

        else:
            context['files'] = self.fm.directory_list()
            context['empty'] = 'Folder is empty'

        return context


class DirectoryCreateView(FilemanagerMixin, FormView):
    template_name = 'filemanager/filemanager_create_directory.html'
    form_class = DirectoryCreateForm
    extra_breadcrumbs = [{
        'path': '#',
        'label': 'Create directory'
    }]

    def get_success_url(self):
        url = '%s?path=%s' % (reverse('administration:directory_list'), self.fm.path)
        if hasattr(self, 'popup') and self.popup:
            url += '&popup=1'
        return url

    def form_valid(self, form):
        self.fm.create_directory(form.cleaned_data.get('directory_name'))
        return super(DirectoryCreateView, self).form_valid(form)


# class FilmList(LoginRequiredMixin, ListView):
#     template_name = 'films.html'
#     model = Film
#     context_object_name = 'films'

#notes

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            context = {"error": "Invalid username or password."}
            return render(request, "accounts/login.html", context)
        login(request, user)
        return redirect('/')
    return render(request, "accounts/login.html", {})



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "accounts/login.html", context)


































