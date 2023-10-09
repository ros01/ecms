from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from .exceptions import DuplicateDocumentNameError, DuplicateFolderNameError
User = get_user_model()
# Create your models here.

class FileInfo(models.Model):
    path = models.URLField()
    info = models.CharField(max_length=255)

    def __str__(self):
        return self.path




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
    path = models.URLField()
    encoded_path = models.FileField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='authors', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    share_with = models.ManyToManyField(User)
    staff_comments = models.ManyToManyField(StaffComments, related_name='staff_comments')
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

    def shared_queryset(self):
        """
        Returns queryset of this folder mapped into the shared user model.
        The queryset should only consist of zero or one instances (aka shared
        or not shared.) This method is mostly used for convenience.
        """
        model = self.shared_user_model()
        return model._default_manager.filter(**{model.obj_attr: self})

    
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
