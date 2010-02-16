from webapp.postosaurus.models import User, Membership, Subscription
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


def emails_from_post(post):
    
    return [email for email in post.keys() if post[email] and email != 'confirmed']


def remove_from_org(email, org):
    
    """
    Removes the member from the organization. Also unsubscribes
    from all lists.
    """
    
    user = mailinglist.find_user(email)
    if user != org.owner:
        membership = Membership.objects.get(organization = org, user=user)
        membership.delete()

        for mlist in org.mailinglist_set.all():
            remove_from_list(email, mlist, org)


def remove_from_list(email, mlist, org):
    sub = mailinglist.find_subscription(email, mlist.name, org)
    if sub:
        sub.delete()
    
            
