from django.conf.urls import patterns, url

from web import aviews
from web.views import index as index_

urlpatterns = patterns('',
	url(r'^raresuffixes/$', aviews.rare_suffixes, name='rare_suffixes'),
    url(r'^$', index_, name='index'),
)
