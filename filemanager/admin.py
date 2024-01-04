from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(FileInfo)
admin.site.register(Document)
admin.site.register(StaffComments)
admin.site.register(Folder)
admin.site.register(SharedDocument)