# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(default=b'', max_length=256, blank=True)),
                ('created', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('username', models.CharField(max_length=255, verbose_name=b'User name')),
                ('email', models.EmailField(max_length=255, verbose_name=b'E Mail')),
                ('iaccept', models.BooleanField(default=True, verbose_name=b'I do accept')),
                ('user_type', models.CharField(max_length=5, verbose_name=b'User type', choices=[(b'ST', b'Student'), (b'CM', b'Company')])),
                ('is_active', models.BooleanField(default=False)),
                ('activation_token', models.CharField(max_length=255, unique=True, null=True, verbose_name=b'Activation token', blank=True)),
                ('activated_at', models.DateTimeField(auto_now=True, verbose_name=b'Activated at')),
                ('approved', models.BooleanField(default=True)),
                ('approved_at', models.DateTimeField(auto_now=True, verbose_name=b'Approved at')),
                ('last_login_at', models.DateTimeField(auto_now=True, verbose_name=b'Updated at')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'Updated at')),
                ('deleted_at', models.DateTimeField(auto_now=True, verbose_name=b'Deleted at')),
                ('is_admin', models.BooleanField(default=False)),
                ('token_generated', models.DateTimeField(null=True, blank=True)),
                ('approved_by', models.ForeignKey(related_name='posted_user', verbose_name=b'Approved by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('created_by', models.ForeignKey(related_name='created_user', verbose_name=b'Created by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('deleted_by', models.ForeignKey(related_name='deleted_user', verbose_name=b'Deleted by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name='updated_user', verbose_name=b'Updated by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name_plural': 'User',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='apikey',
            name='user',
            field=models.OneToOneField(related_name='api_key', to='accounts.UserProfile'),
            preserve_default=True,
        ),
    ]
