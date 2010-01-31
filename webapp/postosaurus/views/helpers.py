from webapp.postosaurus.models import User
from django.contrib.auth.models import User as DjangoUser
from app.model import mailinglist

def create_users(username, email, password):

    """
    Creates the django user object and the
    postosaurus user.
    """

    #never populate the email address of the django model.
    djangouser = DjangoUser.objects.create_user(username, '', password)
    user = mailinglist.create_user(email)
    user.user = djangouser
    djangouser.save()
    user.save()

    return djangouser, user

