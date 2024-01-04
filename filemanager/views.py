import json
import os
from django.conf import settings
from django.db import transaction
import uuid
import csv
from django.http import Http404, FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, ListView
from django.views.generic.base import View
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, HttpResponseRedirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, reverse,redirect
from django.views.generic.detail import BaseDetailView, SingleObjectTemplateResponseMixin
from .models import *
from .forms import *
from filemanager.forms import DirectoryCreateForm, RenameForm
from filemanager.core import Filemanager
import re
from django.contrib import messages 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
)



class FolderCreate(CreateView):
    model = Folder
    form_class = FolderCreateForm
    template_name = "filemanager/folder_create.html"
    parent = None

    def get(self, request, *args, **kwargs):
        if "p" in request.GET:
            qs = self.model.objects.for_user(request.user)
            self.parent = get_object_or_404(qs, pk=request.GET["p"])
        else:
            self.parent = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault("parent", self.parent)
        return super().get_context_data(**kwargs)

    def get_initial(self):
        if self.parent:
            self.initial["parent"] = self.parent
        return super().get_initial()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"folders": self.model.objects.for_user(self.request.user)})
        return kwargs

    def create_folder(self, **kwargs):
        folder = self.model.objects.create(**kwargs)
        # folder.touch(self.request.user)
        # if folder is not amongst anything shared it will share with no
        # users which share will no-op; perhaps not the best way?
        # folder.share(folder.shared_parent().shared_with())
        return folder

    def get_success_url(self):
        return reverse("filemanager:folder_list")

    def form_valid(self, form):
        kwargs = {
            "name": form.cleaned_data["name"],
            "author": self.request.user,
            "parent": form.cleaned_data["parent"],
        }
        self.object = self.create_folder(**kwargs)
        # hookset.folder_created_message(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())



class FolderList(ListView):
    template_name = "filemanager/folder_list.html"
    def get_queryset(self):
        request = self.request
        qs = Folder.objects.filter(author=request.user)
        # query = request.GET.get('q')
        # if query:
        #     qs = qs.filter(name__icontains=query)
        return qs


    # def get_files_from_directory(directory_path):
    #     files = []
    #     for filename in os.listdir(directory_path):
    #         file_path = os.path.join(directory_path, filename)
    #         if os.path.isfile(file_path):
    #             try:
    #                 print( ' > file_path ' + file_path)
    #                 _, extension = os.path.splitext(filename)
    #                 if extension.lower() == '.csv':
    #                     csv_text = convert_csv_to_text(file_path)
    #                 else:
    #                     csv_text = ''

    #                 files.append({
    #                     'file': file_path.split(os.sep + 'media' + os.sep)[1],
    #                     'filename': filename,
    #                     'file_path': file_path,
    #                     'csv_text': csv_text
    #                 })
    #             except Exception as e:
    #                 print( ' > ' +  str( e ) )    
    #     return files

    # def generate_nested_directory(root_path, current_path):
    #     directories = []
    #     for name in os.listdir(current_path):
    #         if os.path.isdir(os.path.join(current_path, name)):
    #             unique_id = str(uuid.uuid4())
    #             nested_path = os.path.join(current_path, name)
    #             nested_directories = generate_nested_directory(root_path, nested_path)
    #             directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
    #     return directories

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     qs = qs.for_user(self.request.user)
    #     return qs

    def get_context_data(self, directory='', **kwargs):
        context = super().get_context_data(**kwargs)
    #     form = DocumentShareForm
    #     media_path = os.path.join(settings.MEDIA_ROOT)
    #     directories = generate_nested_directory(media_path, media_path)
    #     selected_directory = directory

    #     files = []
    #     selected_directory_path = os.path.join(media_path, selected_directory)
    #     if os.path.isdir(selected_directory_path):
    #         files = get_files_from_directory(selected_directory_path)

        breadcrumbs = get_breadcrumbs(self.request)
        # document_filepath = media_path
        # staff_comment = StaffComments.objects.filter(status=2)
        ctx = {
            # 'members': self.object.members(user=self.request.user),
            # 'directories': directories, 
            # 'files': files, 
            # 'selected_directory': selected_directory,
            # 'segment': 'file_manager',
            'breadcrumbs': breadcrumbs,
            # 'form': form,
            # 'document': document,
            # 'staff_comment': staff_comment,
            # "can_share": self.object.can_share(self.request.user),
        }
        context.update(ctx)
        return context




class FolderDetail(DetailView):
    model = Folder
    form = DocumentCreateForm
    share_form = DocumentShareForm
    template_name = "filemanager/folder_detail.html"


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

    def generate_nested_directory(root_path, current_path):
        directories = []
        for name in os.listdir(current_path):
            if os.path.isdir(os.path.join(current_path, name)):
                unique_id = str(uuid.uuid4())
                nested_path = os.path.join(current_path, name)
                nested_directories = generate_nested_directory(root_path, nested_path)
                directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
        return directories

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.for_user(self.request.user)
        return qs

    def get_context_data(self, directory='', **kwargs):
        context = super().get_context_data(**kwargs)
        form = DocumentCreateForm
        share_form = DocumentShareForm
        media_path = os.path.join(settings.MEDIA_ROOT)
        directories = generate_nested_directory(media_path, media_path)
        selected_directory = directory

        files = []
        selected_directory_path = os.path.join(media_path, selected_directory)
        if os.path.isdir(selected_directory_path):
            files = get_files_from_directory(selected_directory_path)

        breadcrumbs = get_breadcrumbs(self.request)
        folder = Folder.objects.filter(author=self.request.user).first()
        # document_filepath = media_path
        staff_files = Document.objects.filter(author=self.request.user)
        # shared_document = SharedDocument.objects.filter(document=staff_files.get_shared_document)
        staff_comment = StaffComments.objects.filter(status=2)
        ctx = {
            # 'members': self.object.members(user=self.request.user),
            'directories': directories, 
            'files': files,
            'folder': folder, 
            'staff_files': staff_files,
            # 'shared_document':shared_document,
            'selected_directory': selected_directory,
            'segment': 'file_manager',
            'breadcrumbs': breadcrumbs,
            'form': form,
            'share_form': share_form,
            'media_path': media_path,
            'selected_directory_path': selected_directory_path,
            # 'document': document,
            'staff_comment': staff_comment,
            # "can_share": self.object.can_share(self.request.user),
        }

        context.update(ctx)
        # print ("Context:", context)
        return context



class DocumentCreate(CreateView):
    model = Document
    form_class = DocumentCreateForm
    template_name = "filemanager/file_create.html"
    parent = None

    def get(self, request, *args, **kwargs):
        if "p" in request.GET:
            qs = self.model.objects.for_user(request.user)
            self.parent = get_object_or_404(qs, pk=request.GET["p"])
        else:
            self.parent = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault("parent", self.parent)
        return super().get_context_data(**kwargs)

    def get_initial(self):
        if self.parent:
            self.initial["parent"] = self.parent
        return super().get_initial()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"folders": self.model.objects.for_user(self.request.user)})
        return kwargs

    def create_folder(self, **kwargs):
        folder = self.model.objects.create(**kwargs)
        # folder.touch(self.request.user)
        # if folder is not amongst anything shared it will share with no
        # users which share will no-op; perhaps not the best way?
        # folder.share(folder.shared_parent().shared_with())
        return folder

    def get_success_url(self):
        return reverse("filemanager:folder_list")

    def form_valid(self, form):
        kwargs = {
            "name": form.cleaned_data["name"],
            "author": self.request.user,
            "parent": form.cleaned_data["parent"],
        }
        self.object = self.create_folder(**kwargs)
        # hookset.folder_created_message(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())


def create_document(request):
    form = DocumentCreateForm
    # path = file_path.replace('%slash%', '/')
    # absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    # file_path = absolute_file_path
    filename = request.FILES.get('file')
    author = request.user
    modified_by = request.user
    folder=Folder.objects.filter(author=author).first()
    print("Filename:", filename)
    print("Form:", form.clean)
    if request.method == 'POST':
        instance = Document.objects.create(
            # path=request.POST.get('path'),
            # encoded_path=request.POST.get('encoded_path'),
            name=filename,
            author=author,
            modified_by=modified_by,
            folder=folder,
            file = request.FILES.get('file'),
        )
        # form = DocumentCreateForm(request.POST, request.FILES)
        # if form.is_valid():
        #     print("Form:", form)
        #     document = form.save()
            # document.name = request.POST.get('filename')
            # print("Filename:", document.name)
            # document.save()
        
        
        messages.success(request, ('Document Creation Successful'))

    return redirect(request.META.get('HTTP_REFERER'))



def add_comment(request, file_path):
    author = request.user
    encoded_path=request.POST.get('encoded_path')

    if request.method == 'POST':
        comments_list = StaffComments.objects.create(
            author=author,
            comments=request.POST.get('comments'), 
            status = 2,
        )
        

        document = Document.objects.filter(encoded_path = encoded_path)[0]
        document.staff_comments.add(comments_list)
        print("Comment:", comments_list)
        messages.success(request, ('Comment added successfully'))

    return redirect(request.META.get('HTTP_REFERER'))



def share_file(request, id):
    form = DocumentShareForm
    # path = file_path.replace('%slash%', '/')
    # absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    # file_path = absolute_file_path
    document = Document.objects.filter(id=id).first()
    filename = request.FILES.get('file')
    shared_by = request.user

    if request.method == 'POST':
        shared_users=request.POST.get('share_with')
        print("User1:", shared_users)
        staff_user= User.objects.filter(id__in=shared_users)
        print("User:", staff_user)
        instance = SharedDocument.objects.create(
            # path=request.POST.get('path'),
            document=document,
            # file=request.POST.get('file'),
            filename=request.POST.get('filename'),
            shared_by=shared_by,
            remarks=request.POST.get('remarks'),
            # shared_with=staff_user,
        )
        # for user in shared_users:
        #     instance.staff_user.add(user)
        instance.share_with.set(staff_user)
        messages.success(request, ('Document Share Successful'))

    return redirect(request.META.get('HTTP_REFERER'))


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
    qs = SharedDocument.objects.filter(share_with__in = users)

    context = {
        'directories': directories, 
        'files': files, 
        'selected_directory': selected_directory,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs,
        'qs': qs,
    }
    return render(request, 'filemanager/shared_files.html', context)


def shared_document_detail(request, id):
    # document = get_object_or_404(Document, encoded_path = file_path)
    # path = file_path.replace('%slash%', '/')
    # absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    # file_path = absolute_file_path
    document = Document.objects.filter(id=id).first()
    shared_document = SharedDocument.objects.filter(document=document.get_shared_document)




    print("Hi:", document)
    context = {
        'document': document,
        'shared_document': shared_document, 
        # 'encoded_path': absolute_file_path,
    }

    
    return render(request, 'filemanager/document_detail.html', context)


class SharedDocumentDetails(DetailView):
    # queryset = StudentIndexing.objects.all()
    template_name = "filemanager/document_detail.html"

    def get_object(self):
        document_id = self.kwargs.get("d_id")
        sdocument_id = self.kwargs.get("s_id")
        obj = get_object_or_404(SharedDocument, document__id = document_id, id = sdocument_id)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['document'] = obj
        return context


    

def add_comment(request, id):
    author = request.user
    encoded_path=request.POST.get('encoded_path')

    if request.method == 'POST':
        comments_list = StaffComments.objects.create(
            author=author,
            comments=request.POST.get('comments'), 
            status = 2,
        )
        

        document = SharedDocument.objects.filter(id=id).first()
        document.staff_comments.add(comments_list)
        print("Comment:", comments_list)
        messages.success(request, ('Comment added successfully'))

    return redirect(request.META.get('HTTP_REFERER'))


def add_comment2(request, file_path):
    author = request.user
    encoded_path=request.POST.get('encoded_path')

    if request.method == 'POST':
        comments_list = StaffComments.objects.create(
            author=author,
            comments=request.POST.get('comments'), 
            status = 2,
        )
        

        document = Document.objects.filter(encoded_path = encoded_path)[0]
        document.staff_comments.add(comments_list)
        print("Comment:", comments_list)
        messages.success(request, ('Comment added successfully'))

    return redirect(request.META.get('HTTP_REFERER'))


def shared_files2(request, directory=''):
    media_path = os.path.join(settings.MEDIA_ROOT)
    directories = generate_nested_directory(media_path, media_path)
    selected_directory = directory

    files = []
    selected_directory_path = os.path.join(media_path, selected_directory)
    if os.path.isdir(selected_directory_path):
        files = get_files_from_directory(selected_directory_path)

    breadcrumbs = get_breadcrumbs(request)
    users = User.objects.filter(email=request.user.email)
    qs = SharedDocument.objects.filter(share_with__in = users)

    context = {
        'directories': directories, 
        'files': files, 
        'selected_directory': selected_directory,
        'segment': 'file_manager',
        'breadcrumbs': breadcrumbs,
        'qs': qs,
    }
    return render(request, 'filemanager/shared_files.html', context)


def share_file2(request, file_path):
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


def file_detail2(request, file_path):
    # document = get_object_or_404(Document, encoded_path = file_path)
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    # file_path = absolute_file_path
    document = SharedDocument.objects.filter(encoded_path = file_path).first()

    print("Hi:", document)
    context = {
        'document': document, 
        'encoded_path': absolute_file_path,
    }

    
    return render(request, 'filemanager/document_detail.html', context)

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
        filename = self.fm.upload_file(filedata = request.FILES)

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

    document = SharedDocument.objects.filter(staff_comments__in=staff_comment)

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


def folder_detail(request, directory=''):
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
    return render(request, 'filemanager/folder_detail.html', context)





class FolderDetails(DetailView):
    model = Folder
    template_name = "filemanager/folder_detail.html"


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

    def generate_nested_directory(root_path, current_path):
        directories = []
        for name in os.listdir(current_path):
            if os.path.isdir(os.path.join(current_path, name)):
                unique_id = str(uuid.uuid4())
                nested_path = os.path.join(current_path, name)
                nested_directories = generate_nested_directory(root_path, nested_path)
                directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
        return directories

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.for_user(self.request.user)
        return qs

    def get_context_data(self, directory='', **kwargs):
        context = super().get_context_data(**kwargs)
        form = DocumentShareForm
        media_path = os.path.join(settings.MEDIA_ROOT)
        directories = generate_nested_directory(media_path, media_path)
        selected_directory = directory

        files = []
        selected_directory_path = os.path.join(media_path, selected_directory)
        if os.path.isdir(selected_directory_path):
            files = get_files_from_directory(selected_directory_path)

        breadcrumbs = get_breadcrumbs(self.request)
        # document_filepath = media_path
        staff_comment = StaffComments.objects.filter(status=2)
        ctx = {
            # 'members': self.object.members(user=self.request.user),
            'directories': directories, 
            'files': files, 
            'selected_directory': selected_directory,
            'segment': 'file_manager',
            'breadcrumbs': breadcrumbs,
            'form': form,
            # 'document': document,
            'staff_comment': staff_comment,
            # "can_share": self.object.can_share(self.request.user),
        }

        context.update(ctx)
        # print ("Context:", context)
        return context


class FileCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentCreateForm
    template_name = "filemanager/file_create.html"
    folder = None

    def get(self, request, *args, **kwargs):
        if "f" in request.GET:
            qs = Folder.objects.for_user(request.user)
            self.folder = get_object_or_404(qs, pk=request.GET["f"])
        else:
            self.folder = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault("folder", self.folder)
        return super().get_context_data(**kwargs)

    def get_initial(self):
        if self.folder:
            self.initial["folder"] = self.folder
        return super().get_initial()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"folders": Folder.objects.for_user(self.request.user)})
        return kwargs

    def create_document(self, **kwargs):
        document = self.model.objects.create(**kwargs)
        document.touch(self.request.user)
        if document.folder is not None:
            # if folder is not amongst anything shared it will share with no
            # users which share will no-op; perhaps not the best way?
            document.share(document.folder.shared_parent().shared_with())
        return document

    def increase_usage(self, bytes):
        # increase usage for this user based on document size
        storage_qs = UserStorage.objects.filter(pk=self.request.user.storage.pk)
        storage_qs.update(bytes_used=F("bytes_used") + bytes)

    def get_create_kwargs(self, form):
        return {
            "name": form.cleaned_data["file"].name,
            # "original_filename": form.cleaned_data["file"].name,
            "folder": form.cleaned_data["folder"],
            "author": self.request.user,
            "file": form.cleaned_data["file"],
        }


    def get_success_url(self):
        return reverse("filemanager:folder_list")

    def form_valid(self, form):
        with transaction.atomic():
            kwargs = self.get_create_kwargs(form)
            # self.object = self.create_file(**kwargs)
            # hookset.document_created_message(self.request, self.object)
            # bytes = form.cleaned_data["file"].size
            # self.increase_usage(bytes)
            return HttpResponseRedirect(self.get_success_url())


class DocumentDetail(DetailView):
    model = Document
    template_name = "filemanager/folder_detail.html"


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

    def generate_nested_directory(root_path, current_path):
        directories = []
        for name in os.listdir(current_path):
            if os.path.isdir(os.path.join(current_path, name)):
                unique_id = str(uuid.uuid4())
                nested_path = os.path.join(current_path, name)
                nested_directories = generate_nested_directory(root_path, nested_path)
                directories.append({'id': unique_id, 'name': name, 'path': os.path.relpath(nested_path, root_path), 'directories': nested_directories})
        return directories

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.for_user(self.request.user)
        return qs

    def get_context_data(self, directory='', **kwargs):
        context = super().get_context_data(**kwargs)
        form = DocumentShareForm
        media_path = os.path.join(settings.MEDIA_ROOT)
        directories = generate_nested_directory(media_path, media_path)
        selected_directory = directory

        files = []
        selected_directory_path = os.path.join(media_path, selected_directory)
        if os.path.isdir(selected_directory_path):
            files = get_files_from_directory(selected_directory_path)

        breadcrumbs = get_breadcrumbs(self.request)
        # document_filepath = media_path
        staff_comment = StaffComments.objects.filter(status=2)
        ctx = {
            # 'members': self.object.members(user=self.request.user),
            'directories': directories, 
            'files': files, 
            'selected_directory': selected_directory,
            'segment': 'file_manager',
            'breadcrumbs': breadcrumbs,
            'form': form,
            # 'document': document,
            'staff_comment': staff_comment,
            # "can_share": self.object.can_share(self.request.user),
        }

        context.update(ctx)
        # print ("Context:", context)
        return context


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


def download_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(absolute_file_path):
        with open(absolute_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_file_path)
            return response
    raise Http404


def download_iframe(request, id):
    obj = Document.objects.get(id=id)
    filename = obj.file.path
    response = FileResponse(open(filename, 'rb'))
    return response



def download(request, id):
    obj = Document.objects.get(id=id)
    filename = obj.file.path
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(absolute_file_path):
        with open(absolute_file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(absolute_file_path)
            return response
    raise Http404


def delete_file(request, id):
    obj = Document.objects.get(id=id)
    obj.delete()
    messages.success(request, ('Document Delete Successful'))
    return redirect(request.META.get('HTTP_REFERER'))










# if request.method == 'POST':

#         batch_list = request.POST.getlist('batch')

#         info = Batch.objects.create(user_id=request.user.id)
#         for item in batch_list:
#             info.material_id.add(item)










        





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





def delete_file2(request, file_path):
    path = file_path.replace('%slash%', '/')
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, path)
    os.remove(absolute_file_path)
    print("File deleted", absolute_file_path)
    return redirect(request.META.get('HTTP_REFERER'))

    


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
    print("File Path:", file_path)
    return redirect(request.META.get('HTTP_REFERER'))


class SharedFiles(ListView):
    template_name = "filemanager/shared_files.html"
    def get_queryset(self):
        request = self.request
        # qs = User.objects.filter(document__in=Document.objects.all())
        qs = Document.objects.filter(share_with__in=User.objects.all())
        query = request.GET.get('q')
        if query:
            qs = qs.filter(name__icontains=query)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(SharedFiles, self).get_context_data(*args, **kwargs)

        media_path = os.path.join(settings.MEDIA_ROOT)
        directories = generate_nested_directory(media_path, media_path)
        selected_directory = directory
        files = []
        selected_directory_path = os.path.join(media_path, selected_directory)
        if os.path.isdir(selected_directory_path):
            files = get_files_from_directory(selected_directory_path)
            breadcrumbs = get_breadcrumbs(self.request)

        # context['directories'] = directories  
        context['files'] = files
        context['selected_directory'] = selected_directory
        context['segment'] = segment
        context['breadcrumbs'] = breadcrumbs
        return context


class ViewProfile(TemplateView):
    template_name = "filemanager/viewprofile.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(ViewProfile, self).get_context_data(*args, **kwargs)
        return context

class AllFiles(TemplateView):
    template_name = "filemanager/admin_files.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(AllFiles, self).get_context_data(*args, **kwargs)
        return context

class FilesGroup(TemplateView):
    template_name = "filemanager/files_group_view.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(FilesGroup, self).get_context_data(*args, **kwargs)
        return context

class FilesList(TemplateView):
    template_name = "filemanager/files_list_view.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(FilesList, self).get_context_data(*args, **kwargs)
        return context
       
class StarredFiles(TemplateView):
    template_name = "filemanager/starred_files.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(StarredFiles, self).get_context_data(*args, **kwargs)
        return context


class SharedOutgoing(TemplateView):
    template_name = "filemanager/shared_outgoing.html"

    
    def get_context_data(self, *args, **kwargs):
        context = super(SharedOutgoing, self).get_context_data(*args, **kwargs)


class SharedLinks(TemplateView):
    template_name = "filemanager/shared_links.html"

    def get_context_data(self, *args, **kwargs):
        context = super(SharedLinks, self).get_context_data(*args, **kwargs)

class RecoverFiles(TemplateView):
    template_name = "filemanager/recovery.html"

    def get_context_data(self, *args, **kwargs):
        context = super(RecoverFiles, self).get_context_data(*args, **kwargs)



class FileSettings(TemplateView):
    template_name = "filemanager/setting.html"

    def get_context_data(self, *args, **kwargs):
        context = super(FileSettings, self).get_context_data(*args, **kwargs)



class MailBox(TemplateView):
    template_name = "filemanager/mailbox.html"

    def get_context_data(self, *args, **kwargs):
        context = super(MailBox, self).get_context_data(*args, **kwargs)


