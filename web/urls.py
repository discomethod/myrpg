from django.conf.urls import patterns, url

from web import views

urlpatterns = patterns('',
    url(r'^items/(?P<item_id>\d+)/$', views.item, name='item'),
    url(r'^items/gen/$', views.item_gen, name='item_gen'),
    url(r'^items/$', views.item_list, name='item_list'),
    url(r'^affixes/g/(?P<affix_group_id>\d+)/$', views.affix_group, name='affix_group'),
    url(r'^affixes/(?P<affix_id>\d+)/$', views.affix, name='affix'),
    url(r'^affixes/$', views.affix_list, name='affix_list'),
    url(r'^characters/create/$', views.character_create, name="character_create"),
    url(r'^accounts/login/$', views.login_view, name='login'),
    url(r'^accounts/logout/$', views.logout_view, name='logout'),
    url(r'^$', views.index, name='index')
)
