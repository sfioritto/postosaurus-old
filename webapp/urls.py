from django.conf.urls.defaults import *
from django.conf import settings

handler500 = 'webapp.postosaurus.views.server_error'
handler404 = 'webapp.postosaurus.views.page_not_found'


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',

    (r'^$', 'webapp.postosaurus.views.index'),
    (r'^landing/(\d+)/$', 'webapp.postosaurus.views.landing'),
    (r'^signup/$', 'webapp.postosaurus.views.create_list'),
    (r'^app/', include('webapp.postosaurus.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

)

if settings.DEBUG:
    urlpatterns += patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_DOC_ROOT}),)


