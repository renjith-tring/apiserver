from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.conf import settings
from django.core.validators import RegexValidator
import datetime,re
from django.utils import timezone
USER_ROLE = (('ST','Student'),('CM','Company'))


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, user_type, iaccept, password=None):
        if not username:
            raise ValueError('Users must have an e-mail address')

        user = self.model(username = username, email = email, user_type = user_type, iaccept = iaccept)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, user_type, iaccept, password):
        user = self.create_user(username, email, user_type, iaccept, password = password,)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user
        
    def verify_user(self, verification_code):
        if re.match('[a-f0-9]{40}', verification_code):
            try:
                user = self.get(activation_token=verification_code)
                print user
            except self.model.DoesNotExist:
                return False
                print "FDSFsd"
            if not user.verification_code_expired():
                # Account exists and has a non-expired key. Activate it.
                user.is_active = True
                user.save()
                return True
            return False


class UserProfile(AbstractBaseUser):
    username            = models.CharField(verbose_name='User name', max_length=255, blank=False, null=False)
    email               = models.EmailField(verbose_name='E Mail', max_length=255,blank=False, null=False)
    iaccept             = models.BooleanField(default=True, blank=False, null=False, verbose_name='I do accept')
    user_type           = models.CharField(verbose_name="User type", max_length=5, choices=USER_ROLE, blank=False, null=False)
    is_active           = models.BooleanField(default=False)
    activation_token    = models.CharField(verbose_name='Activation token', max_length=255, unique=True, blank=True, null=True)
    activated_at        = models.DateTimeField(verbose_name='Activated at', auto_now=True)
    approved            = models.BooleanField(default=True)
    approved_at         = models.DateTimeField(verbose_name='Approved at', auto_now=True)
    approved_by         = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = 'Approved by', related_name = 'posted_user', blank = True, null = True)
    last_login_at       = models.DateTimeField(verbose_name='Updated at', auto_now=True)
    created_at          = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    created_by          = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Created by', related_name='created_user', blank = True, null = True)
    updated_at          = models.DateTimeField(verbose_name='Updated at', auto_now=True)
    updated_by          = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Updated by', related_name='updated_user', blank = True, null = True)
    deleted_at          = models.DateTimeField(verbose_name='Deleted at', auto_now=True)
    deleted_by          = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Deleted by', related_name='deleted_user', blank = True, null = True)
    is_admin            = models.BooleanField(default=False, blank=True)
    token_generated     = models.DateTimeField(null=True,blank=True) 
    
    objects             = MyUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name_plural = u'User'


    def __str__(self):
        return self.username


    def verification_code_expired(self):
        expiration_date = datetime.timedelta(days=15)
        return self.token_generated + expiration_date <= timezone.now()

