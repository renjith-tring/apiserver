from django.conf.urls import url, include
from tastypie.api import Api
from apps.accounts.api import UserResource
from apps.accounts import signals

v1_api = Api(api_name='v1')
v1_api.register(UserResource())

urlpatterns = [
    url(r'^api/', include(v1_api.urls)),
    url(
        r'^reset/(?P<uidb36>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
        'reset_confirm', 
         name='password_reset_confirm'
        ),

   	url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
	  'django.contrib.auth.views.password_reset_confirm',
	 {'post_reset_redirect': '/accounts/password/done/'},),
]