from django.contrib.auth.models import User as DjangoUser
from webapp.postosaurus.models import User as PostUser


class SettingsBackend:

    """
    Authenticates against postosaurus users, not django
    users.
    """

    def authenticate(self, username=None, password=None):
        try:
            puser = PostUser.objects.get(pk=username)
            user = puser.user
            print user.check_password(password)
            if user and user.check_password(password):
                return user
            else:
                return None
        except PostUser.DoesNotExist:
            return None


    def get_user(self, user_id):
        try:
            return DjangoUser.objects.get(pk=user_id)
        except PostUser.DoesNotExist:
            return None
