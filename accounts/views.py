from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.views.generic import (
     CreateView,
     DetailView,
     ListView,
     UpdateView,
     DeleteView,
     TemplateView
)
from django.views import View
from django.contrib.auth import get_user_model, update_session_auth_hash, authenticate, login as auth_login
from django.contrib import messages, auth
from .forms import SignupForm

User = get_user_model()

AUTH_USER_MODEL = 'accounts.User'



class SignUpView(View):
    form_class = SignupForm
    template_name = 'accounts/register.html'
    template_name1 = 'accounts/account_creation_confirmation.html'
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():    
            user = form.save(commit=False)
            #user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            return render(request, self.template_name1)
        return render(request, self.template_name, {'form': form})


# class Profile(DetailView):
#     model = models.User
#     slug_field = 'username'
#     def get_context_data(self, request, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['username'] = request.user.username
#         return context
#     def get_success_url(self):
#         return reverse_lazy('accounts:profile', kwargs={'slug': self.username})

class LoginTemplateView(TemplateView):
    template_name = "accounts/login.html"


def login(request):
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']
    user = auth.authenticate(email=email, password=password)
    if user is not None:
        auth_login(request, user)
        if user.department == 'ICT':
            return redirect('sys_admin:sys_admin_dashboard')
        if user.department == 'Admin':
            return redirect('admin_dp:admin_dashboard')
        if user.department == 'Monitoring':
            return redirect('monitoring:monitoring_dashboard')
        if user.department == 'Protocol':
            return redirect('protocol_unit:protocol_dashboard')
        if user.department == 'Procurement':
            return redirect('procurement_unit:procurement_dashboard')
        if user.department == 'Registration':
            return redirect('registration:registration_dashboard')
        if user.department == 'Registrars Office':
            return redirect('registrar_office:registrar_office_dashboard')
        if user.department == 'Finance':
            return redirect('faa:faa_dashboard')
        if user.department == 'Planning':
            return redirect('planning_dp:planning_dashboard')
        if user.department == 'Legal':
            return redirect('legal_unit:legal_dashboard')
        if user.department == 'Servicom':
            return redirect('servicom_unit:servicom_dashboard')
        if user.department == 'Audit':
            return redirect('audit_unit:audit_dashboard')
        if user.department == 'Institute':
            return redirect('institute:institute_dashboard')
        if user.department == 'Stores':
            return redirect('stores:stores_dashboard')
        else:
            messages.error(request, 'Please enter the correct email and password for your account. Note that both fields may be case-sensitive.')
            return redirect('accounts:signin')
    else:
        messages.error(request, 'Please enter the correct email and password for your account. Note that both fields may be case-sensitive.')
        return redirect('accounts:signin')


def logout(request):
  if request.method == 'POST':
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('index')