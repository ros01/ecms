from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model


class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        return self._create_user(email, password, **extra_fields)

    
class User(AbstractBaseUser, PermissionsMixin):

    DEPARTMENT = (
        ('Monitoring', 'Monitoring'),
        ('Registrations', 'Registrations'),
        ('Admin', 'Admin'),
        ('Procurement', 'Procurement'),
        ('Finance', 'Finance'),
        ('Audit', 'Audit'),
        ('ICT', 'ICT'),
        ('Stores', 'Stores'),
        ('Institute', 'Institute'),
        ('Protocol', 'PR & Protocol'),
        ('Registrars Office', 'Registrars Office'),
        )

    ZONE = (
        ('HQ', 'HQ'),
        ('Lagos Zonal Office ', 'Lagos Zonal Office'),
        ('Lagos CERT-RADMIRS', 'Lagos CERT-RADMIRS'),
        ('Asaba', 'Asaba'),
        ('Enugu', 'Enugu'),
        ('Port Harcourt', 'Port Harcourt'),
        ('Kano', 'Kano'),
        ('Sokoto', 'Sokoto'),
        ('Nnewi', 'Nnewi'),
        ('Calabar', 'Calabar'),
        )
   
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_no = models.CharField(max_length=100, blank=True)
    department = models.CharField (max_length=30, choices = DEPARTMENT,  null=True, blank=True)
    zone = models.CharField(max_length=120, choices=ZONE,  null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    is_hod = models.BooleanField(
        _('HOD'),
        default=True,
        help_text=_(
            'Designates whether this user should be given HOD rights. '),
    )

    
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    #def get_absolute_url(self):
        #return reverse("accounts:profile_detail", kwargs={"id": self.id})

    def __str__(self):
        return self.email
   
    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.email

    def reg_date_pretty(self):
        return self.date_joined .strftime('%b %e %Y')