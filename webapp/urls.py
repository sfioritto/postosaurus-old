from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

handler500 = 'webapp.postosaurus.views.server_error'
handler404 = 'webapp.postosaurus.views.page_not_found'
handler403 = 'webapp.postosaurus.views.permission_denied'
admin.autodiscover()

urlpatterns = patterns(
    '',

    (r'^$', 'webapp.postosaurus.views.index'),
    (r'^landing/$', 'webapp.postosaurus.views.landing'),
    (r'^signup/$', 'webapp.postosaurus.views.create_list'),
    (r'^app/', include('webapp.postosaurus.urls')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_DOC_ROOT}),)


