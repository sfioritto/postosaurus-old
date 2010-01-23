from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^lists/(?P<listname>.+)/links/$', 'webapp.postosaurus.views.links'),
    (r'^lists/(?P<listname>.+)/files/$', 'webapp.postosaurus.views.files'),
    (r'^lists/(?P<listname>.+)/members/$', 'webapp.postosaurus.views.members'),
    (r'^lists/(?P<listname>.+)/tasks/$', 'webapp.postosaurus.views.tasks'),
    (r'^lists/(?P<listname>.+)/archive/$', 'webapp.postosaurus.views.archive_overview'),
    (r'^lists/(?P<listname>.+)/archive/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/$', 
     'webapp.postosaurus.views.archive_by_day'),
    (r'^lists/create/$', 'webapp.postosaurus.views.create_list'),
    (r'^user/create/$', 'webapp.postosaurus.views.create_user'),
    (r'^user/$', 'webapp.postosaurus.views.user_main'),
    (r'^user/profile/$', 'webapp.postosaurus.views.user_profile'),
    (r'^user/password/$', 'webapp.postosaurus.views.user_password'),
    (r'^user/billing/$', 'webapp.postosaurus.views.user_billing'),
    (r'^thanks/$', 'webapp.postosaurus.views.list_created'),
    (r'^login/$', 'django.contrib.auth.views.login', {
            'template_name': 'postosaurus/login.html'
            }),
    (r'logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'subscriptions/create/(?P<planid>.+)/$', 'webapp.postosaurus.views.create_subscription'),
    (r'subscriptions/update/$', 'webapp.postosaurus.views.update_subscriptions'),
    (r'contact/$', 'webapp.postosaurus.views.contact'),
)
