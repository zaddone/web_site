from django.conf.urls import patterns, url
urlpatterns = patterns('website.views',
                       url(r'^find_city/$','find_city'),
                       url(r'^themedetail/$', 'site_theme_page', name='theme_page'),   
                       
                       #url(r'^page/$', 'life_page'),    
                       url(r'^page-(?P<query>[\S\s-]+).html$', 'life_page',{'template_name':'showpage.html'}), 

                       url(r'^aboutus/$', 'about_us_page',{'template_name':'aboutus.html'}),     
                       
            
                       url(r'^choice/$', 'life_oneday',{'template_name':'showchoice.html'}), 
                       url(r'^choice/(?P<query>[\S-]+)/$', 'life_oneday',{'template_name':'showchoice.html'}), 
                       url(r'^app/$', 'life_app',{'template_name':'showhome.html'}), 
                       url(r'^(?P<query>[\S-]+)/$', 'tag_city_page',{'template_name':'showlist.html'}), 
                       
                       url(r'^$', 'tag_city_page',{'template_name':'showlist.html'}), 
                       )