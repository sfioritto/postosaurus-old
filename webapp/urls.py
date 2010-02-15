from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

handler500 = 'webapp.postosaurus.views.server_error'
handler404 = 'webapp.postosaurus.views.page_not_found'
handler403 = 'webapp.postosaurus.views.permission_denied'
admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^$', 'webapp.postosaurus.views.marketing.index'),
    (r'^plans/$', 'webapp.postosaurus.views.marketing.plans'),
    (r'^user/create/$', 'webapp.postosaurus.views.user.create_user'),
    (r'^user/billing/$', 'webapp.postosaurus.views.spreedly.billing'),
    (r'^user/settings/$', 'webapp.postosaurus.views.user.settings'),
    (r'^login/$', 'django.contrib.auth.views.login', {
            'template_name': 'postosaurus/login.html'
            }),
    (r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'^subscriptions/create/(?P<planid>.+)/$', 'webapp.postosaurus.views.spreedly.create_subscription'),
    (r'^subscriptions/update/$', 'webapp.postosaurus.views.spreedly.update_subscriptions'),
    (r'^org/', include('webapp.postosaurus.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^contact/', 'webapp.postosaurus.views.marketing.contact'),
    (r'^faq/', 'webapp.postosaurus.views.marketing.faq'),
    (r'^about/', 'webapp.postosaurus.views.marketing.about'),
    (r'^privacy/', 'webapp.postosaurus.views.marketing.privacy'),
    )

if settings.TEMPLATE_DEBUG:
    urlpatterns += patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_DOC_ROOT}),)


