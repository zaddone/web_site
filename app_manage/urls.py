from django.conf.urls import patterns, url
urlpatterns = patterns('app_manage.views',
    url(r'^share-(?P<query>[\S\s-]+).html$','showCont',{'template_name':'share_showEvent.html'}),
    url(r'^app-(?P<query>[\S\s-]+).html$','showCont'),
    url(r'^q-(?P<query>[\S\s-]+).html$','showQ',{'template_name':'q_showEvent.html'}),
    url(r'^html/(?P<app>[\d-]+)/$', 'app_manage',  ),      
    url(r'^json/(?P<app>[\d-]+)/$', 'app_manage_api',  ),                 
    url(r'^html/$', 'app_manage',  ),      
    url(r'^json/$', 'app_manage_api',  ), 
    url(r'^download/$','download_file')   
    #url(r'^update/$','update'),
)
