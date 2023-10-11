from django.shortcuts import render, redirect
import os
import uuid
import csv
from accounts.forms import SignupForm
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
from filemanager.models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
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



class DashboardView(TemplateView):
    #template_name = "administration/admin_dept_dashboard_main.html"
    template_name = "sys_admin/sys_admin_dashboard.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(DashboardView, self).get_context_data(*args, **kwargs)
        return context


def convert_csv_to_text(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    text = ''
    for row in rows:
        text += ','.join(row) + '\n'

    return text

def get_files_from_directory(directory_path):
    files = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            try:
                print( ' > file_path ' + file_path)
                _, extension = os.path.splitext(filename)
                if extension.lower() == '.csv':
                    csv_text = convert_csv_to_text(file_path)
                else:
                    csv_text = ''

                files.append({
                    'file': file_path.split(os.sep + 'media' + os.sep)[1],
                    'filename': filename,
                    'file_path': file_path,
                    'csv_text': csv_text
                })
            except Exception as e:
                print( ' > ' +  str( e ) )    
    return files


def get_breadcrumbs(request):
    path_components = [component for component in request.path.split("/") if component]
    breadcrumbs = []
    url = ''

    for component in path_components:
        url += f'/{component}'
        if component == "file-manager":
            component = "media"
        breadcrumbs.append({'name': component, 'url': url})

    return breadcrumbs


def generate_nested_directory(root_path, current_path):
    directories = []
    for name in os.listdir(current_path):
        if os.path.isdir(os.path.join(current_path, name)):
            unique_id = str(uuid.uuid4())
            nested_path = os.path.join(current_path, name)
            nested_directories = generate_nested_directory(root_path, nested_path)
            directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
    return directories


def shared_files(request, directory=''):
    media_path = os.path.join(settings.MEDIA_ROOT)
    directories = generate_nested_directory(media_path, media_path)
    selected_directory = directory

    files = []
    selected_directory_path = os.path.join(media_path, selected_directory)
    if os.path.isdir(selected_directory_path):
        files = get_files_from_directory(selected_directory_path)

    breadcrumbs = get_breadcrumbs(request)
    users = User.objects.filter(email=request.user.email)
    qs = Document.objects.filter(share_with__in = users)

    user = request.user
    # qs= user.documents.all()

    context = {
        'directories': directories, 
        'files': files, 
        'selected_directory': selected_directory,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs,
        'qs': qs,
    }
    return render(request, 'sys_admin/shared_files.html', context)


def download_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(absolute_file_path):
        with open(absolute_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_file_path)
            return response
    raise Http404


class RecoverFiles(TemplateView):
    template_name = "sys_admin/recovery.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RecoverFiles, self).get_context_data(*args, **kwargs)



class FileSettings(TemplateView):
    template_name = "sys_admin/setting.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FileSettings, self).get_context_data(*args, **kwargs)



class SharedOutgoing(TemplateView):
    template_name = "sys_admin/shared_outgoing.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(SharedOutgoing, self).get_context_data(*args, **kwargs)



class UserCreateView(CreateView):
	form_class = SignupForm
	template_name = 'sys_admin/create_user.html'
	template_name1 = 'sys_admin/user_creation_confirmation.html'
	# success_url = reverse_lazy('accounts:profile')

	success_message = "%(last_name)s User Profile was created successfully"


	# def get_success_url(self):
    #     return reverse_lazy('accounts:profile', kwargs={'slug': self.username})

	def get_success_message(self, cleaned_data):
		return self.success_message % dict(
            cleaned_data,
            last_name=self.object.last_name,
        )

	def get(self, request, *args, **kwargs):
		# user_form = self.user_form()
		form  = self.form_class()
		return render(request, self.template_name, {'form':form})

	def post(self, request, *args, **kwargs):
		# user_form = self.user_form(request.POST)
		form  = self.form_class (request.POST)
		
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = True
			user.save()
			return render(request, self.template_name1)
			# indexing_officer = form.save(commit=False)
			# IndexingOfficerProfile.objects.create(
            #     indexing_officer = user,
            #     institution = indexing_officer.institution,
            #     )
			# indexing_officer = IndexingOfficerProfile.objects.filter(indexing_officer=user).first()
			# user = user
			# reset_password(user, request)
			# return redirect(indexing_officer.get_absolute_url())

	   	# 	return redirect('index')  	
	   	
		# print(request.POST)
		return render(request, self.template_name, {'form':form})









