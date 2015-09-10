from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'life_site.views.home', name='home'),
    # url(r'^life_site/', include('life_site.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    #url(r'^explorer/', include('explorer_resume.urls')),
    #url(r'^website/',include('website.urls')),
    url(r'^app/', include('app_manage.urls')),
    url(r'^', include('website.urls'), name='home'),
)
