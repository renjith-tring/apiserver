from django.conf.urls import url, include
from tastypie.api import Api
from apps.accounts.api import UserResource
from apps.accounts import signals

v1_api = Api(api_name='v1')
v1_api.register(UserResource())

urlpatterns = [
    url(r'^api/', include(v1_api.urls)),
]