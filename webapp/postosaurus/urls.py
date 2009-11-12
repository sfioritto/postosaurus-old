from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^lists/(?P<listid>\d+)/links/$', 'webapp.postosaurus.views.links'),
    (r'^lists/(?P<listid>\d+)/archive/$', 'webapp.postosaurus.views.archive'),
    (r'^lists/create/$', 'webapp.postosaurus.views.create_list'),
    (r'^outofspace/$', 'webapp.postosaurus.views.out_of_space'),
    (r'^thanks/$', 'webapp.postosaurus.views.list_created'),
)
