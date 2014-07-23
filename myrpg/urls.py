from django.conf.urls import include, patterns, url

handler404 = 'myrpg.views.error404'
handler500 = 'myrpg.views.error500'

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myrpg.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include('web.aurls')),
    url(r'^', include('web.urls')),
)
