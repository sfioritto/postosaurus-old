from django.conf import settings

def media_url(request):
    return {'MEDIA_URL': settings.MEDIA_URL}
