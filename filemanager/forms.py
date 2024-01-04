from django import forms
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()



class FolderCreateForm(forms.ModelForm):

    class Meta:
        model = Folder
        fields = ["name", "parent"]
        widgets = {
            "parent": forms.HiddenInput,
        }

    def clean(self):
        name = self.cleaned_data["name"]
        parent = self.cleaned_data.get("parent")
        if Folder.already_exists(name, parent):
            raise forms.ValidationError(f"{name} already exists.")

    def __init__(self, *args, **kwargs):
        folders = kwargs.pop("folders")
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = folders


class DocumentCreateForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ["file", "folder"]
        widgets = {
            "folder": forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        # folders = kwargs.pop("folders")
        # self.storage = kwargs.pop("storage")
        super().__init__(*args, **kwargs)
        # self.fields["folder"].queryset = folders

    # def clean_file(self):
    #     value = self.cleaned_data["file"]
    #     if (value.size + self.storage.bytes_used) > self.storage.bytes_total:
    #         raise forms.ValidationError("File will exceed storage capacity.")
    #     return value

    def clean(self):
        if "file" in self.cleaned_data:
            name = self.cleaned_data.get("file").name
            folder = self.cleaned_data.get("folder")
            if Document.already_exists(name, folder):
                raise forms.ValidationError(
                    hookset.already_exists_validation_message(name, folder)
                )
                       
class DirectoryCreateForm(forms.Form):
    directory_name = forms.CharField()


class RenameForm(forms.Form):
    input_name = forms.CharField()
    old_name = forms.CharField()



class UserMultipleChoiceField(forms.ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return user_display(obj)


class FolderShareForm(forms.Form):

    participants = UserMultipleChoiceField(
        queryset=None,
        widget=forms.SelectMultiple(
            attrs={
                "class": "span6",
                "data-placeholder": "Choose participants... "
            }
        )
    )



class DocumentShareForm(forms.ModelForm):

    # def label_from_instance(self, obj):
    #     return "%s (%s)" % (obj.get_full_name(), obj.username)

    share_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
         model = SharedDocument
         fields = ('filename', 'shared_by', 'share_with', 'remarks')  

    def __init__(self, *args, **kwargs):
       super(DocumentShareForm, self).__init__(*args, **kwargs)
       self.fields['share_with'].label_from_instance = lambda obj: "%s" % obj.get_full_name()









































