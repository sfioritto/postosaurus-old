from django.core.exceptions import PermissionDenied


def authorize_or_raise(user, org):

    """
    Very simple authorization. This checks to see if the user is a member
    of the list and raises a permission denied error if they aren't.
    """

    if not user.in_org(org):
        raise PermissionDenied
