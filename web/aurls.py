from django.conf.urls import include, patterns, url
from django.contrib import admin

from web import aviews

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^raresuffixes/$', aviews.rare_suffixes, name="rare_suffixes"),
    url(r'^', include(admin.site.urls)),
)
