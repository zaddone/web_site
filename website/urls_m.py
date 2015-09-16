from django.conf.urls import patterns, url
urlpatterns = patterns('website.views',
                       url(r'^find_city/$','find_city'),
                       url(r'^themedetail/$', 'site_theme_page', name='theme_page'),
                       url(r'^map/(?P<query>[\S\s-]+)/$', 'view_map',{'template_name':'m_showmap.html'}),
                       url(r'^page-(?P<query>[\S\s-]+).html$', 'life_page',{'template_name':'m_showpage.html'}), 
                       url(r'^(?P<query>[\S-]+)/$', 'tag_city_page',{'template_name':'m_showlist.html'}), 
                       url(r'^$', 'tag_city_page',{'template_name':'m_showlist.html'}), 
                    )