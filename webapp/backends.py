from django.conf import settings
from django.contrib.auth.models import User as DjangoUser
from webapp.models import User as PostUser


class SettingsBackend:

    """
    Authenticates against postosaurus users, not django
    users.
    """

    def authenticate(self, username=None, password=None):
        try:
            user = DjangoUser.objects.get(pk=username)
            if user.check_password(password):
                return user
        except DjangoUser.DoesNotExist:
            return None


    def get_user(self, user_id):
        try:
            return PostUser.objects.get(pk=user_id)
        except PostUser.DoesNotExist:
            return None
