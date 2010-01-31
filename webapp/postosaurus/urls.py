from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^lists/(?P<listname>.+)/links/$', 'webapp.postosaurus.views.org.links'),
    (r'^lists/(?P<listname>.+)/files/$', 'webapp.postosaurus.views.org.files'),
    (r'^lists/(?P<listname>.+)/members/$', 'webapp.postosaurus.views.org.members'),
    (r'^lists/(?P<listname>.+)/tasks/$', 'webapp.postosaurus.views.org.tasks'),
    (r'^lists/(?P<listname>.+)/archive/$', 'webapp.postosaurus.views.list.archive_overview'),
    (r'^lists/(?P<listname>.+)/archive/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/$', 
     'webapp.postosaurus.views.list.archive_by_day'),
    (r'^user/create/$', 'webapp.postosaurus.views.user.create_user'),
    (r'^user/$', 'webapp.postosaurus.views.user.user_settings'),
    (r'^user/billing/$', 'webapp.postosaurus.views.user.user_billing'),
    (r'^login/$', 'django.contrib.auth.views.login', {
            'template_name': 'postosaurus/login.html'
            }),
    (r'logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'subscriptions/create/(?P<planid>.+)/$', 'webapp.postosaurus.views.spreedly.create_subscription'),
    (r'subscriptions/update/$', 'webapp.postosaurus.views.spreedly.update_subscriptions'),
)
