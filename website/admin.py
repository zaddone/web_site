#coding:utf-8
from django.contrib import admin
from website.models import links_page_info,url_page_info
class linksPageInfoAdmin(admin.ModelAdmin):
    pass
    #raw_id_fields = ['img']
    
class urlPageInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(links_page_info, linksPageInfoAdmin)
admin.site.register(url_page_info, linksPageInfoAdmin)