from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .choices import * 


from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

from django.contrib.auth import get_user_model
User = get_user_model()


class SignupForm(UserCreationForm):
    department = forms.ChoiceField(choices = DEPARTMENT, widget=forms.Select(), required=True)
    zone = forms.ChoiceField(choices = ZONE, widget=forms.Select(), required=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_no', 'department', 'zone', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
       super(SignupForm, self).__init__(*args, **kwargs)
       self.fields['first_name'].label = "First Name"
       self.fields['first_name'].widget.attrs['placeholder'] = "Enter First Name"
       self.fields['last_name'].label = "Last Name"
       self.fields['last_name'].widget.attrs['placeholder'] = "Enter Last Name"
       self.fields['phone_no'].label = "Phone Number"
       self.fields['phone_no'].widget.attrs['placeholder'] = "Enter Phone Number"
       self.fields['department'].label = "Department"
       self.fields['zone'].label = "Zone"
       self.fields['email'].label = "Email"
       self.fields['email'].widget.attrs['placeholder'] = "Enter Email"