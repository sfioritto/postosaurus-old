from django.shortcuts import render_to_response
from django.template import RequestContext

def page_not_found(request):
    #Handles 404 errors
    return render_to_response('postosaurus/404.html', context_instance = RequestContext(request))


def server_error(request):
    #Handles 500 errors
    return render_to_response('postosaurus/500.html', context_instance = RequestContext(request))

def permission_denied(request):
    #Handles 403 errors
    return render_to_response('postosaurus/403.html', context_instance = RequestContext(request))
