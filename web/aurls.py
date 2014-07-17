from django.conf.urls import patterns, url

from web import aviews

urlpatterns = patterns('',
    url(r'^raresuffixes/$', aviews.rare_suffixes, name="rare_suffixes"),
    url(r'^$', aviews.index, name='index'),
)
