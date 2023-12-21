from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from .exceptions import DuplicateDocumentNameError, DuplicateFolderNameError
from django.db.models.query import QuerySet
User = get_user_model()
import itertools
import operator

from django.apps import apps
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.utils.text import slugify
# Create your models here.

class FileInfo(models.Model):
    path = models.URLField()
    info = models.CharField(max_length=255)

    def __str__(self):
        return self.path


class FolderManager(models.Manager):

    def members(self, folder, **kwargs):
        direct = kwargs.get("direct", True)
        user = kwargs.get("user")
        # Document = apps.get_model("documents", "Document")
        folders = self.filter(parent=folder)
        documents = Document.objects.filter(folder=folder)
        if user:
            folders = folders.for_user(user)
            # documents = documents.for_user(user)
        M = sorted(itertools.chain(folders, documents), key=operator.attrgetter("name"))
        if direct:
            return M
        for child in folders:
            M.extend(self.members(child, **kwargs))
        return M


class FolderQuerySet(QuerySet):

    def for_user(self, user):
        """
        All folders the given user can do something with.
        """
        # def for_user(self, user):
        return self.filter(author=user)
        # qs = SharedMemberQuerySet(model=self.model, using=self._db, user=user)
        # qs = qs.filter(Q(author=user) | Q(foldershareduser__user=user))
        # return qs.distinct() & self.distinct()


class SharedMemberQuerySet(QuerySet):

    def __init__(self, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(**kwargs)

    def iterator(self):
        shared_user_model = self.model.shared_user_model()
        shared_members = shared_user_model.for_user(self.user)
        for obj in super().iterator():
            if obj.pk in shared_members:
                obj._shared = True
            yield obj

    def _chain(self, **kwargs):
        kwargs["user"] = self.user
        return super()._chain(**kwargs)



class Folder(models.Model):
    name = models.CharField(max_length=140)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    slug   = models.SlugField(blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE, null=True)

    objects = FolderManager.from_queryset(FolderQuerySet)()

    kind = "folder"
    icon = "folder-open"
    shared = None

    # @classmethod
    # def shared_user_model(cls):
    #     return FolderSharedUser

    # @classmethod
    # def already_exists(cls, name, parent=None):
    #     return cls.objects.filter(name=name, parent=parent).exists()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.pk and Folder.already_exists(self.name, self.parent):
            raise DuplicateFolderNameError(f"{self.name} folder already exists.")
        self.touch(self.author, commit=False)
        super().save(**kwargs)

    
    def get_absolute_url(self):
        # return reverse("filemanager:folder_list")
        return reverse("filemanager:folder_detail", kwargs={"slug": self.slug})

    def unique_id(self):
        return "f-%d" % self.id

    def members(self, **kwargs):
        return Folder.objects.members(self, **kwargs)


    def touch(self, user, commit=True):
        self.modified = timezone.now()
        self.modified_by = user
        if commit:
            if self.parent:
                self.parent.touch(user)
            self.save()

    @classmethod
    def already_exists(cls, name, folder=None):
        return cls.objects.filter(name=name, folder=folder).exists()

def pre_save_folder_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)

pre_save.connect(pre_save_folder_receiver, sender=Folder)


class FileDetail(models.Model):
    name = models.URLField()
    # path = models.URLField()
    # encoded_path = models.FileField()
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.CASCADE)
    # file = models.FileField(upload_to=uuid_filename)
    file = models.FileField(upload_to='%Y/%m/%d/', blank=True, null=True)
    
    # original_filename = models.CharField(max_length=500)

    # objects = DocumentQuerySet.as_manager()

    kind = "document"
    icon = "file"
    shared = None

    def delete(self, *args, **kwargs):
        bytes_to_free = self.size
        super().delete(*args, **kwargs)
        storage_qs = UserStorage.objects.filter(pk=self.author.storage.pk)
        storage_qs.update(bytes_used=F("bytes_used") - bytes_to_free)

    @classmethod
    def shared_user_model(cls):
        return DocumentSharedUser

    @classmethod
    def already_exists(cls, name, folder=None):
        return cls.objects.filter(name=name, folder=folder).exists()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.pk and FileDetail.already_exists(self.name, self.folder):
            raise DuplicateDocumentNameError(f"{self.name} already exists in this folder.")
        self.touch(self.author, commit=False)
        super().save(**kwargs)

    def get_absolute_url(self):
        return reverse("filemanager:file_detail", args=[self.pk])

    def unique_id(self):
        return "d-%d" % self.id

    def touch(self, user, commit=True):
        self.modified = timezone.now()
        self.modified_by = user
        if commit:
            if self.folder:
                self.folder.touch(user)
            self.save()

    @property
    def size(self):
        return self.file.size

    def breadcrumbs(self):
        crumbs = []
        if self.folder:
            crumbs.extend(self.folder.breadcrumbs())
            crumbs.append(self.folder)
        return crumbs

    def shared_queryset(self):
        """
        Returns queryset of this folder mapped into the shared user model.
        The queryset should only consist of zero or one instances (aka shared
        or not shared.) This method is mostly used for convenience.
        """
        model = self.shared_user_model()
        return model._default_manager.filter(**{model.obj_attr: self})

    @property
    def shared(self):
        """
        Determines if self is shared. This checks the denormalization and
        does not return whether self SHOULD be shared (based on parents.)
        """
        return self.shared_queryset().exists()

    def shared_ui(self):
        return False

    def shared_with(self, user=None):
        """
        Returns a User queryset of users shared on this folder, or, if user
        is given optimizes the check and returns boolean.
        """
        User = get_user_model()
        qs = self.shared_queryset()
        if user is not None:
            return qs.filter(user=user).exists()
        if not qs.exists():
            return User.objects.none()
        return User.objects.filter(pk__in=qs.values("user"))

    def share(self, users):
        users = [u for u in users if not self.shared_with(user=u)]
        if users:
            model = self.shared_user_model()
            objs = []
            for user in users:
                objs.append(self.shared_user_model()(**{model.obj_attr: self, "user": user}))
            model._default_manager.bulk_create(objs)

    def download_url(self):
        return reverse(
            "filemanager:download_file",
            args=[self.pk]
        )

    def delete_url(self):
        return reverse(
            "filemanager:delete_file",
            args=[self.pk]
        )


class StaffComments(models.Model):
    comments = models.TextField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    status = models.IntegerField(default=1)


    def __str__(self):
        return str(self.status)


    


class Document(models.Model):
    filename = models.CharField(max_length=255)
    # folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE)
    path = models.URLField()
    encoded_path = models.FileField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='authors', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    share_with = models.ManyToManyField(User, related_name='shared_users')
    staff_comments = models.ManyToManyField(StaffComments)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    

    def __str__(self):
        return self.filename

    # def save(self, **kwargs):
    #     if not self.pk and Document.already_exists(self.filename, self.folder):
    #         raise DuplicateDocumentNameError(f"{self.filename} already exists in this folder.")
    #     self.touch(self.author, commit=False)
    #     super().save(**kwargs)

    # def get_absolute_url(self):
    #     return reverse("filemanager:document_detail", args=[self.pk])

    # def shared_queryset(self):
        """
        Returns queryset of this folder mapped into the shared user model.
        The queryset should only consist of zero or one instances (aka shared
        or not shared.) This method is mostly used for convenience.
        """
        # model = self.shared_user_model()
        # return model._default_manager.filter(**{model.obj_attr: self})

    
    # def shared_with(self, user=None):
        """
        Returns a User queryset of users shared on this folder, or, if user
        is given optimizes the check and returns boolean.
        """
        # User = get_user_model()
        # qs = self.shared_queryset()
        # if user is not None:
        #     return qs.filter(user=user).exists()
        # if not qs.exists():
        #     return User.objects.none()
        # return User.objects.filter(pk__in=qs.values("user"))
