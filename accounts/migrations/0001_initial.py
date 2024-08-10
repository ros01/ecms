# Generated by Django 4.2.5 on 2024-01-04 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=30)),
                ('phone_no', models.CharField(blank=True, max_length=100)),
                ('department', models.CharField(blank=True, choices=[('Monitoring', 'Monitoring'), ('Registrations', 'Registrations'), ('Admin', 'Admin'), ('Procurement', 'Procurement'), ('Finance', 'Finance'), ('Audit', 'Audit'), ('ICT', 'ICT'), ('Stores', 'Stores'), ('Institute', 'Institute'), ('Protocol', 'PR & Protocol'), ('Registrars Office', 'Registrars Office')], max_length=30, null=True)),
                ('zone', models.CharField(blank=True, choices=[('HQ', 'HQ'), ('Lagos Zonal Office ', 'Lagos Zonal Office'), ('Lagos CERT-RADMIRS', 'Lagos CERT-RADMIRS'), ('Asaba', 'Asaba'), ('Enugu', 'Enugu'), ('Port Harcourt', 'Port Harcourt'), ('Kano', 'Kano'), ('Sokoto', 'Sokoto'), ('Nnewi', 'Nnewi'), ('Calabar', 'Calabar')], max_length=120, null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_hod', models.BooleanField(default=True, help_text='Designates whether this user should be given HOD rights. ', verbose_name='HOD')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
