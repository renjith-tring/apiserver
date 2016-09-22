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
from apps.accounts.models import UserProfile
import sha, random, datetime, json
from django.contrib.auth.hashers import make_password
from .custom.exceptions import *


class UserResource(ModelResource):

	class Meta:
		queryset = UserProfile.objects.all()
		allowed_methods = ['get', 'post', 'patch']
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

			url(r"^(?P<resource_name>%s)/verify/(?P<activation_token>\w[\w/-]*)%s$" %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('email_verify'), name="email_verify"),

			url(r"^(?P<resource_name>%s)/signin%s$" %(self._meta.resource_name, trailing_slash()),
				self.wrap_view('signin'), name="api_signin"),

			url(r'^(?P<resource_name>%s)/logout%s$' %
				(self._meta.resource_name, trailing_slash()),
				self.wrap_view('logout'), name='api_logout'),

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
		if data.has_key('username') and data.has_key('password'):
			username = data.get('username')
			password = data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return self.create_response(request, {'success': True,"message":"successfully logined"})
				else:
					# Return a 'disabled account' error message
					return self.create_response(request, {'status': False,"message":"User is not active please verify your mal"})
			else:
				# Return an 'invalid login' error message.
				return self.create_response(request, {'status': False,"message":"no permission"})
		else:
			return self.create_response(request, {'success': False,"message":"please enter valid data"})

	def logout(self, request, **kwargs):
		if logout(request):
			return self.create_response(request, {'status': True,"message":"Successfully loged out"})
		else:
			data = {"status":"Error","message":"somthing went wrong"}
			return self.error_response(request,data)
		# else:
		# 	return HttpResponse(json.dumps({ 'success': False }))

