#coding:utf-8
from django.contrib import admin
from store.models import storeInfo
class storeInfoAdmin(admin.ModelAdmin):
    pass

admin.site.register(storeInfo,storeInfoAdmin )

