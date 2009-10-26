from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^lists/create/$', 'webapp.postosaurus.views.create_list'),
    (r'^thanks/$', 'webapp.postosaurus.views.list_created'),
)
