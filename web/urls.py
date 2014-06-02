from django.conf.urls import patterns, url

from web import views

urlpatterns = patterns('',
    url(r'^item/(?P<item_id>\d+)/$', views.item, name='item'),
    url(r'^item/gen/$', views.itemgen, name='itemgen'),
    url(r'^item/$', views.itemlist, name='itemlist'),
    url(r'^affixes/g/(?P<affixgroup_id>\d+)/$', views.affixgroup, name='affixgroup'),
    url(r'^affixes/(?P<affix_id>\d+)/$', views.affix, name='affix'),
    url(r'^affixes/$', views.affixlist, name='affixlist'),
    url(r'^$', views.index, name='index')
)

