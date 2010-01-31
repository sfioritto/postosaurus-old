from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^links/$', 'webapp.postosaurus.views.org.links'),
    (r'^files/$', 'webapp.postosaurus.views.org.files'),
    (r'^members/$', 'webapp.postosaurus.views.org.members'),
    (r'^tasks/$', 'webapp.postosaurus.views.org.tasks'),
    (r'^lists/(?P<listname>.+)/archive/$', 'webapp.postosaurus.views.list.archive_overview'),
    (r'^lists/(?P<listname>.+)/archive/(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)/$', 
     'webapp.postosaurus.views.list.archive_by_day'),
    (r'^user/create/$', 'webapp.postosaurus.views.user.create_user'),
    (r'^user/$', 'webapp.postosaurus.views.user.main'),
    (r'^user/settings/$', 'webapp.postosaurus.views.user.settings'),
    (r'^user/billing/$', 'webapp.postosaurus.views.spreedly.billing'),
    (r'^login/$', 'django.contrib.auth.views.login', {
            'template_name': 'postosaurus/login.html'
            }),
    (r'logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'subscriptions/create/(?P<planid>.+)/$', 'webapp.postosaurus.views.spreedly.create_subscription'),
    (r'subscriptions/update/$', 'webapp.postosaurus.views.spreedly.update_subscriptions'),
)
