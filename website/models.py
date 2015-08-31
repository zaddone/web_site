#coding:utf-8
from django.db import models
from base.models import storeImg

class links_page_info(models.Model):
    url = models.CharField(u'url',max_length=100, unique=True)
    title = models.CharField(u'title',max_length=100)
    img = models.ForeignKey(storeImg,blank=True,null=True,verbose_name=u'图片')
    description = models.CharField(u'description',max_length=500,blank=True,)
    order= models.IntegerField(u'order',blank=True,)
    def __unicode__(self):
        return self.title
    class Meta:
        db_table = 'page_info_links'      
        verbose_name = u'友链'
        verbose_name_plural = u'友链'
        app_label='web_site'
    
class url_page_info(models.Model):
    url = models.CharField(u'url',max_length=100, unique=True)
    title = models.CharField(u'title',max_length=100)
    keywords = models.CharField(u'keywords',max_length=100,blank=True)
    description = models.CharField(u'description',max_length=500,blank=True)
    links=models.ManyToManyField(links_page_info,verbose_name=u'友链',blank=True,)
    
    def __unicode__(self):
        return self.title
    class Meta:
        db_table = 'page_info_url'
        verbose_name = u'页面信息'
        verbose_name_plural = u'页面信息'
        app_label='web_site'