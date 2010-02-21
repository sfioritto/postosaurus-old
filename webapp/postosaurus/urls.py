from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/$', 'webapp.postosaurus.views.org.main'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/activate/$', 'webapp.postosaurus.views.spreedly.activate_org'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/members/$', 'webapp.postosaurus.views.org.members'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/members/$', 'webapp.postosaurus.views.list.members'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/members/edit$', 'webapp.postosaurus.views.list.edit_members'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/members/invite$', 'webapp.postosaurus.views.list.invite_member'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/files/$', 'webapp.postosaurus.views.list.files'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/files/upload/$', 'webapp.postosaurus.views.list.upload_file'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/files/(?P<filename>.+)/$', 'webapp.postosaurus.views.list.file_versions'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/archive/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/$', 
     'webapp.postosaurus.views.list.archive_by_day'),
    (r'^(?P<orgname>[-a-zA-Z0-9]+)/lists/(?P<listname>.+)/archive/$', 'webapp.postosaurus.views.list.archive_overview'),
)
