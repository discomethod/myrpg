from django.conf.urls import patterns, url

from web import views

urlpatterns = patterns('',
    url(r'^item/(?P<item_id>\d+)/$', views.item, name='item'),
    url(r'^item/gen/$', views.item_gen, name='item_gen'),
    url(r'^item/$', views.item_list, name='item_list'),
    url(r'^affixes/g/(?P<affix_group_id>\d+)/$', views.affix_group, name='affix_group'),
    url(r'^affixes/(?P<affix_id>\d+)/$', views.affix, name='affix'),
    url(r'^affixes/$', views.affix_list, name='affix_list'),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url(r'^$', views.index, name='index')
)
