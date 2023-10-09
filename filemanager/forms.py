from django import forms
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()


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
         model = Document
         fields = ('filename', 'path', 'encoded_path', 'author', 'share_with', 'remarks')  

    def __init__(self, *args, **kwargs):
       super(DocumentShareForm, self).__init__(*args, **kwargs)
       self.fields['share_with'].label_from_instance = lambda obj: "%s" % obj.get_full_name()









































