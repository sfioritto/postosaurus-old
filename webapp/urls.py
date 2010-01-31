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
    (r'^app/', include('webapp.postosaurus.urls')),
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


