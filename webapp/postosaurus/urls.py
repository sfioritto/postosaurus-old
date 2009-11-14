from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^users/(?P<userid>\w+)/lists/(?P<listid>\d+)/links/(?P<pagenum>\d+)/$', 'webapp.postosaurus.views.links'),
    (r'^users/(?P<userid>\w+)/lists/(?P<listid>\d+)/manage/$', 'webapp.postosaurus.views.manage_list'),
    (r'^subscribers/(?P<subid>\d+)/remove/manager/$', 'webapp.postosaurus.views.delete_subscription'),
    (r'^subscribers/(?P<subid>\d+)/remove/user/(?P<userid>\d+)/$', 'webapp.postosaurus.views.user_delete_subscription'),
    (r'^users/?P<userid>>\d+/lists/(?P<listid>\d+)/archive/$', 'webapp.postosaurus.views.archive'),
    (r'^lists/create/$', 'webapp.postosaurus.views.create_list'),
    (r'^users/(?P<userid>\w+)/account', 'webapp.postosaurus.views.userprofile'),
    (r'^outofspace/$', 'webapp.postosaurus.views.out_of_space'),
    (r'^thanks/$', 'webapp.postosaurus.views.list_created'),
)
