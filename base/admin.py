#coding:utf-8
from django.contrib import admin
from base.models import storeImg,storeServer
class storeImgAdmin(admin.ModelAdmin):
    pass

class storeServerAdmin(admin.ModelAdmin):
    pass

admin.site.register(storeImg,storeImgAdmin )
admin.site.register(storeServer,storeServerAdmin )
