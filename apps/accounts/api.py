from django.core.exceptions  import ValidationError
from tastypie.resources import ModelResource,Resource
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie import fields, utils
from django.conf.urls import patterns, include, url
from django.contrib.auth import authenticate, login, logout
from tastypie.exceptions import BadRequest
from django.conf.urls import patterns, url
from django.http import HttpResponse
from tastypie.utils import trailing_slash
from apps.accounts.models import UserProfile, ApiKey
import sha, random, datetime, json
from django.contrib.auth.hashers import make_password
from .custom.exceptions import *
import uuid
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from apps.accounts.forms import PasswordResetForm

class UserResource(ModelResource):

	class Meta:
		queryset = UserProfile.objects.all()
		allowed_methods = ['post']
		resource_name = 'user'
		excludes = ('id', 'passowrd')
		authorization = Authorization()
		include_resource_uri = False
		always_return_data = True
		fields = ['email', 'username']

	def obj_get(self, bundle, **kwargs):
		request_user = kwargs['pk']
		bundle_obj = super(UserResource, self).obj_get(bundle, **kwargs)
		return bundle_obj

	def obj_create(self, bundle, **kwargs):
		REQUIRED_FIELDS = ('username','email','user_type','password')
		for field in REQUIRED_FIELDS:
			if field not in bundle.data:
				raise CustomBadRequest(
					code='missing_key',
					message=('Must provide {missing_key} when creating a'
							 ' user.').format(missing_key=field))

		email               = bundle.data['email']
		username            = bundle.data['username']
		user_type           = bundle.data['user_type']
		kwargs["password"]  = make_password(bundle.data['password'])
		token_generated     = datetime.datetime.now()
		salt                = sha.new(str(random.random())).hexdigest()[:5]
		activation_token    = sha.new(salt+username).hexdigest()
		
		## Password Validation

		# if not validate_password(raw_password):
		#   raise CustomBadRequest(
		#       code='invalid_password',
		#       message='Your password is invalid.')

		## Add password to kwargs
		# kwargs["password"] = make_password(raw_password)

		try:
			if UserProfile.objects.filter(email=email) and UserProfile.objects.filter(username= username):
				raise CustomBadRequest(
					code='duplicate_exception',
					message='That email or username is already associated with some user.')
		except UserProfile.DoesNotExist:
			pass
		bundle_obj = super(UserResource, self).obj_create(bundle,token_generated=token_generated, activation_token=activation_token,**kwargs)
		return bundle_obj


	def prepend_urls(self):
		return [

			## Email Verification
			url(r"^(?P<resource_name>%s)/verify/(?P<activation_token>\w[\w/-]*)%s$" %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('email_verify'), name="email_verify"),

			## User Login
			url(r"^(?P<resource_name>%s)/signin%s$" %(self._meta.resource_name, trailing_slash()),
				self.wrap_view('signin'), name="api_signin"),

			## User Log out
			url(r'^(?P<resource_name>%s)/logout%s$' %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('logout'), name='api_logout'),

			## Change Password
			url(r'^(?P<resource_name>%s)/changepassword%s$' %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('change_password'), name='change_password'),

			## Reset Links for Forget password
			url(r'^(?P<resource_name>%s)/mail_token%s' %(self._meta.resource_name, trailing_slash()),
				self.wrap_view('mail_token'), name='api_passwordreset_mail_token'),

			## Change the password
			url(r'(?P<resource_name>%s)/passwordchange/(?P<mail_token>\w[\w/-]*)%s$'% (self._meta.resource_name, trailing_slash()),
				self.wrap_view('change'), name='api_passwordreset_change'),

			]


	def email_verify(self, request, **kwargs):
		if kwargs.has_key('activation_token'):
			token = kwargs.get('activation_token',None)
			verification_key = token.lower()
			account = UserProfile.objects.verify_user(verification_key)
			if account:
				data = {"status":"success","message":"successfully verified email"}
			else:
				data = {"status":"error","message":"something went wrong"}
			return self.create_response(request,data)
		else:
			data = {"status":"Error","message":"somthing went wrong"}
			return self.error_response(request,data)
	
	def signin(self, request, **kwargs):

		data = json.loads(request.body)
		# user_type = request.POST['user_type']
		REQUIRED_FIELDS = ('username','password')
		for field in REQUIRED_FIELDS:
			if field not in data:
				raise CustomBadRequest(
					code='missing_key',
					message=('Must provide {missing_key} when try to login'
							 ' user.').format(missing_key=field))
		if data.has_key('username') and data.has_key('password'):
			username = data.get('username')
			password = data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					api_user = ApiKey.objects.get(user=user)
					token = api_user.key
					return self.create_response(request, {'success': True,"message":"successfully logined",'username':request.user.username,'token':token})
				else:
					# Return a 'disabled account' error message
					return self.create_response(request, {'status': False,"message":"User is not active please verify your mal"})
			else:
				# Return an 'invalid login' error message.
				return self.create_response(request, {'status': False,"message":"no permission"})
		else:
			return self.create_response(request, {'success': False,"message":"please enter valid data"})

	def logout(self, request, **kwargs):
		logout(request)
		return self.create_response(request, {'status': True,"message":"{0} Successfully loged out" .format(username)}) 
	
	@staticmethod
	def is_user_authenticated(apiKey):
		apiKey = str(apiKey)
		try:
			ApiKey.objects.get(key=apiKey)
			return True
		except ObjectDoesNotExist:
			return False
	@staticmethod
	def verifying(apiKey):
		apiKey = str(apiKey)
		try:
			user_api = ApiKey.objects.get(key=apiKey)
			user = UserProfile.objects.get(id=user_api.user.id)
			return user
		except ObjectDoesNotExist:
			return False

	def change_password(self,request,**kwargs):
		REQUIRED_FIELDS = ('api_token','oldpassword', 'newpwd', 'confirmpwd')
		data = json.loads(request.body)
		for field in REQUIRED_FIELDS:
			if field not in data:
				raise CustomBadRequest(
					code='missing_key',
					message=('Must provide {missing_key} when try to change password').format(missing_key=field))
		if data.has_key('api_token'):
			if self.is_user_authenticated(data.get('api_token')):
				user = self.verifying(data.get('api_token'))
				if user.check_password(data.get('oldpassword')):
					print user.username
					if data.get('newpwd') == data.get('confirmpwd'):
						conpwd = data.get('confirmpwd')
						user.set_password(conpwd)
						user.save()
						return self.create_response(request, {'status': True,"message":"{0} successfully change the password" .format(user.username)})
					else:
						return self.create_response(request, {'status': False,"message":" newpassword and confirm password should be same"})
				else:
					return self.create_response(request, {'status': False,"message":" Wrong old password"})
			else:
				return self.create_response(request, {'status': False,"message":" API token not found"})
		else:
			return self.create_response(request, {'status': False,"message":"Missing Api token"})


	def mail_token(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		self.throttle_check(request)
 
		# this metod comes from PostMixin and handles
		# the deserialization + validation boilerplate
		data = json.loads(request.body)

		form = PasswordResetForm({'email': data.get('email')})
		if form.is_valid():
			form.save()
			return self.create_response(request, {'message': 'Email successfully sent.'})
		return self.error_response(request, {'message', 'Error processing the password reset.'})
 
	def change(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		self.throttle_check(request)
		data = json.loads(request.body)
		UserModel = UserProfile()
		try:
			# token itself contains a hyphen so it's important to limit the split

			if kwargs.has_key('mail_token'):
				uidb64, token = kwargs.get('mail_token').split('-', 1)
				assert uidb64 is not None and token is not None
				uid = urlsafe_base64_decode(uidb64)
				user = UserModel._default_manager.get(pk=uid)
		except (AssertionError, TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
			user = None
 
		if user is not None and default_token_generator.check_token(user, token):
			if data.get('new_password') == data.get('new_password_again'):
				user.set_password(data.get('new_password_again'))
				user.save()
				return self.create_response(request, {'message': 'Password reset successful.'})
		return self.error_response(request, {'message': 'Error during password reset.'})