from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

handler404 = 'myrpg.views.error404'
handler500 = 'myrpg.views.error500'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myrpg.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^a/', include('web.aurls')),
    url(r'^', include('web.urls')),
)
