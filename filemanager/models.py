from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from .exceptions import DuplicateDocumentNameError, DuplicateFolderNameError

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


    def __str__(self):
        return str(self.author)


class Document(models.Model):
    name = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)
    commented = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comments_by', blank=True, null=True)
    staff_comments = models.ForeignKey(StaffComments, on_delete=models.CASCADE, null=True) 
    

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.pk and Document.already_exists(self.name, self.folder):
            raise DuplicateDocumentNameError(f"{self.name} already exists in this folder.")
        self.touch(self.author, commit=False)
        super().save(**kwargs)

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
