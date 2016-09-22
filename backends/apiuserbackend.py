from django.contrib.auth.models import check_password
from apps.accounts.models import UserProfile

class ApiUserBackend:
    def authenticate(self, username=None, password=None):

        try:
            # Try to find a user matching your username
            user = UserProfile.objects.get(username=username)
            #  Check the password is the reverse of the username
            if check_password(password, user.password):
                # Yes? return the Django user object
                return user
            else:
                # No? return None - triggers default login failed
                return None
        except UserProfile.DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None

    # Required for your backend to work properly - unchanged in most scenarios
    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            return None
