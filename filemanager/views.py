import json
import os
from django.conf import settings
import uuid
import csv
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, ListView
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, reverse,redirect
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from .models import *
from .forms import *
from filemanager.forms import DirectoryCreateForm, RenameForm
from filemanager.core import Filemanager
import re
from django.contrib import messages 
from django.contrib.messages.views import SuccessMessageMixin

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
                            with open('media/'+file['filepath']) as f:
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


class DetailView(FilemanagerMixin, JSONResponseMixin, TemplateView, SingleObjectTemplateResponseMixin):
    template_name = 'filemanager/browser/filemanager_detail.html'

    # def get_context_data(self, **kwargs):
    #     context = super(DetailView, self).get_context_data(**kwargs)
    #
    #     context['file'] = self.fm.file_details()
    #
    #     return context

    def render_to_response(self, context, **response_kwargs):
        context['file'] = self.fm.file_details()
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context['file'])
        else:
            return super().render_to_response(context)

    # def get(self, request, *args, **kwargs):
    #
    #     return JsonResponse({'data':'james'})

class UploadView(FilemanagerMixin, TemplateView):
    template_name = 'filemanager/filemanager_upload.html'
    extra_breadcrumbs = [{
        'path': '#',
        'label': 'Upload'
    }]


class UploadFileView(FilemanagerMixin, View):
    def post(self, request, *args, **kwargs):
        if len(request.FILES) != 1:
            return HttpResponseBadRequest("Just a single file please.")

        # TODO: get filepath and validate characters in name, validate mime type and extension
        filename = self.fm.upload_file(filedata = request.FILES['files[]'])

        return HttpResponse(json.dumps({
            'files': [{'name': filename}],
        }))


class DirectoryCreateView(FilemanagerMixin, FormView):
    template_name = 'filemanager/filemanager_create_directory.html'
    form_class = DirectoryCreateForm
    extra_breadcrumbs = [{
        'path': '#',
        'label': 'Create directory'
    }]

    def get_success_url(self):
        url = '%s?path=%s' % (reverse('filemanager:browser'), self.fm.path)
        if hasattr(self, 'popup') and self.popup:
            url += '&popup=1'
        return url

    def form_valid(self, form):
        self.fm.create_directory(form.cleaned_data.get('directory_name'))
        return super(DirectoryCreateView, self).form_valid(form)

class RenameView(FilemanagerMixin, FormView):
    template_name = 'filemanager/rename_modal.html'
    form_class = RenameForm
    extra_breadcrumbs = [{
        'path': '#',
        'label': 'Rename'
    }]

    def get_success_url(self):
        url = '%s?path=%s' % (reverse('filemanager:browser'), self.fm.path)
        if hasattr(self, 'popup') and self.popup:
            url += '&popup=1'
        return url

    def form_valid(self, form):
        self.fm.rename(form.cleaned_data.get('old_name'), form.cleaned_data.get('input_name'))

        return super(RenameView, self).form_valid(form)

class DeleteView(FilemanagerMixin,View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        json_data = json.loads(request.body)
        try:
            for files in json_data['files']:
                self.fm.remove(files)

        except Exception as e:
            print(e)
        return HttpResponse('success')

class FileShareView(FilemanagerMixin, FormView):
    template_name = 'filemanager/filemanager_create_directory.html'
    form_class = DirectoryCreateForm
    extra_breadcrumbs = [{
        'path': '#',
        'label': 'Create directory'
    }]

    def get_success_url(self):
        url = '%s?path=%s' % (reverse('filemanager:browser'), self.fm.path)
        if hasattr(self, 'popup') and self.popup:
            url += '&popup=1'
        return url

    def form_valid(self, form):
        self.fm.create_directory(form.cleaned_data.get('directory_name'))
        return super(FileShareView, self).form_valid(form)



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


def file_manager(request, directory=''):
    form = DocumentShareForm
    media_path = os.path.join(settings.MEDIA_ROOT)
    directories = generate_nested_directory(media_path, media_path)
    selected_directory = directory

    files = []
    selected_directory_path = os.path.join(media_path, selected_directory)
    if os.path.isdir(selected_directory_path):
        files = get_files_from_directory(selected_directory_path)

    breadcrumbs = get_breadcrumbs(request)
    # document_filepath = media_path
    staff_comment = StaffComments.objects.filter(status=2) 

    document = Document.objects.filter(staff_comments__in=staff_comment)

    context = {
        'directories': directories, 
        'files': files, 
        'selected_directory': selected_directory,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs,
        'form': form,
        'document': document,
        'staff_comment': staff_comment,
        'is_htmx': True
    }
    return render(request, 'filemanager/file_dirs.html', context)


def files_manager(request, directory=''):
    media_path = os.path.join(settings.MEDIA_ROOT)
    directories = generate_nested_directory(media_path, media_path)
    selected_directory = directory

    files = []
    selected_directory_path = os.path.join(media_path, selected_directory)
    if os.path.isdir(selected_directory_path):
        files = get_files_from_directory(selected_directory_path)

    breadcrumbs = get_breadcrumbs(request)

    context = {
        'directories': directories, 
        'files': files, 
        'selected_directory': selected_directory,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs,
        'is_htmx': True
    }
    return render(request, 'partials/folder_docs.html', context)




def generate_nested_directory(root_path, current_path):
    directories = []
    for name in os.listdir(current_path):
        if os.path.isdir(os.path.join(current_path, name)):
            unique_id = str(uuid.uuid4())
            nested_path = os.path.join(current_path, name)
            nested_directories = generate_nested_directory(root_path, nested_path)
            directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
    return directories


def save_info(request, file_path):
    path = file_path.replace('%slash%', '/')
    if request.method == 'POST':
        FileInfo.objects.update_or_create(
            path=path,
            defaults={
                'info': request.POST.get('info')
            }
        )
    
    return redirect(request.META.get('HTTP_REFERER'))



def share_file(request, file_path):
    form = FolderShareForm
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    file_path = absolute_file_path
    filename = request.FILES.get('file')
    author = request.user

    if request.method == 'POST':
        shared_users=request.POST.get('share_with')
        print("User1:", shared_users)
        staff_user= User.objects.filter(id__in=shared_users)
        print("User:", staff_user)
        instance = Document.objects.create(
            path=request.POST.get('path'),
            encoded_path=request.POST.get('encoded_path'),
            filename=request.POST.get('filename'),
            author=author,
            remarks=request.POST.get('remarks'),
            # shared_with=staff_user,
        )
        # for user in shared_users:
        #     instance.staff_user.add(user)
        instance.share_with.set(staff_user)
        messages.success(request, ('Document Share Successful'))

    return redirect(request.META.get('HTTP_REFERER'))

# if request.method == 'POST':

#         batch_list = request.POST.getlist('batch')

#         info = Batch.objects.create(user_id=request.user.id)
#         for item in batch_list:
#             info.material_id.add(item)

def add_comment(request, file_path):
    author = request.user
    encoded_path=request.POST.get('encoded_path')

    if request.method == 'POST':
        comments_list = StaffComments.objects.create(
            author=author,
            comments=request.POST.get('comments'),
            status = 2,  
        )

        document = Document.objects.get(encoded_path = encoded_path)
        document.staff_comments.add(comments_list)
        print("Comment:", comments_list)
        messages.success(request, ('Comment added successfully'))

    return redirect(request.META.get('HTTP_REFERER'))



def file_detail(request, file_path):
    document = get_object_or_404(Document, encoded_path = file_path)
    context = {
        'document': document, 
    }
    return render(request, 'filemanager/document_detail.html', context)
        





    # def form_valid(self, form):
    #     org = form.cleaned_data.get('organization')
    #     emails = form.cleaned_data.get("share_email_with")

    #     users = User.objects.filter(email__in=emails)
    #     instance = Setupuser.objects.create(organization=org)

    #     instance.emails_for_help.set(users)

    #     return redirect("/")





    # document = get_object_or_404(Document, pk=pk)
    # document.users.add(request.user)
    # context = {'document': document}
    # return render(request, 'partials/shared_list.html', context)





def delete_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    os.remove(absolute_file_path)
    print("File deleted", absolute_file_path)
    return redirect(request.META.get('HTTP_REFERER'))

    
def download_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(absolute_file_path):
        with open(absolute_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_file_path)
            return response
    raise Http404

def upload_file(request):
    media_path = os.path.join(settings.MEDIA_ROOT)
    selected_directory = request.POST.get('directory', '') 
    selected_directory_path = os.path.join(media_path, selected_directory)
    if request.method == 'POST':
        file = request.FILES.get('file')
        file_path = os.path.join(selected_directory_path, file.name)
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    return redirect(request.META.get('HTTP_REFERER'))

