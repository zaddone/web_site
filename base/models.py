#coding:utf-8
from django.db import models
import ftplib,time,os
from django.contrib.auth.models import User
try:
    from PIL import Image
except:
    import Image

class storeTag(models.Model):
    ct=(
        (0,u'形容词'),
        (1,u'动词'),
        (2,u'名词'), 
      )
    #cat_id = models.AutoField(primary_key=True)
    name = models.CharField(u'名称',max_length=100, unique=True)
    sex=models.IntegerField(u'type',choices=ct,default=0)
    hot= models.IntegerField(u'热度', blank=True,null=True)
    def __unicode__(self):
        return self.name


    class Meta:
        # managed = False
        db_table = 'store_tag'      
        verbose_name = u'标签词库'
        verbose_name_plural = u'标签词库'
        app_label='web_site'


class storeServer(models.Model): 
    name=models.CharField(u'服务器地址',max_length=200,blank=True, null=True)
    def __unicode__(self):
        return self.name 
    class Meta:
        # managed = False
        db_table = 'store_file_server'
        verbose_name = u'资源服务器'
        verbose_name_plural = u'资源服务器'
        app_label='web_site'


class storeFile(models.Model):
    name=models.CharField(u'文件名称', max_length=50, blank=True)
    urls = models.CharField(u'文件url', max_length=200, blank=True)
    file = models.FileField(u'文件',upload_to = 'temp',blank=True)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
    last_time = models.DateTimeField(auto_now=True,verbose_name=u'最后编辑时间')
    server=models.ForeignKey(storeServer,blank=True, verbose_name=u'服务器地址')
    order=models.IntegerField(u'排序',blank=True )
    size= models.IntegerField(u'大小',blank=True )
    def __unicode__(self):
        return "%s%s" % (self.server.name if self.server else 'http://pic1.qkan.com/' ,self.urls)
    
    def get_ftp_obj(self,_dir='storeFile',server='pic1.qkan.com',uid='imga',pwd='b@Veryevent'):
        #Inductive arrangement file in ftp,Modify self.urls
        
        try:
            s = ftplib.FTP(server,uid,pwd)
        except ftplib.error_perm:
            return False
        try:   
            s.cwd(_dir)   
        except ftplib.error_perm:   
            s.mkd(_dir)
        curTime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        curTime=str(curTime)
        try:   
            s.cwd(curTime)   
        except ftplib.error_perm:
            s.mkd(curTime)  
            try:
                s.cwd(curTime)
            except:
                pass
        self.urls=os.path.join(_dir,curTime)
        return s
    def post_ftp(self,ftp_obj,file_name):
        f = open(self.file.path,'rb') 
        ftp_obj.storbinary('STOR '+file_name, f)
        f.close()
    def close_ftp(self,ftp_obj):
        ftp_obj.quit()
        
    def ftp_file_name(self,_dir):
        try:
            base, ext = os.path.splitext(os.path.basename(self.file.path))
        except:
            return None
        if not self.name:
            self.name=base
        filename=_dir+str(self.pk)+ext
        self.urls=os.path.join(self.urls,filename)
        self.size=os.path.getsize(self.file.path)
        
        return filename
        
    def save(self,file_dir= 'storeFile'):
        super(storeFile, self).save()          
        
        
        filename=self.ftp_file_name(_dir = file_dir)
        s=self.get_ftp_obj(_dir=file_dir)
        if s:
            
            self.post_ftp(s,filename)
            self.close_ftp(s)
            super(storeFile, self).save()
        
    class Meta:
        # managed = False
        db_table = 'store_file'
        verbose_name = u'文件'
        verbose_name_plural = u'文件'
        app_label='web_site'


class storeImg(storeFile):
    
    width=models.IntegerField(u'图片宽度',blank=True, )
    height=models.IntegerField(u'图片高度', blank=True, )
    
    def post_ftp(self,ftp_obj,file_name={}):
        for fi in file_name:            
            f = open(file_name[fi],'rb') 
            ftp_obj.storbinary('STOR '+fi, f)
            f.close()
    def scale_dimensions(self,max_width=1080,filename_thumbnail=None):
        
        obj_img = Image.open(self.file.path)
        (width, height) = obj_img.size
        if width > max_width:
            ratio = max_width*1./width
            width = max_width
            height = int(height*ratio)
            obj_img.thumbnail((width, height), Image.ANTIALIAS)
            if filename_thumbnail:
                path=os.path.split(self.file.path)[0];
                filename_thumbnail = os.path.join(path,filename_thumbnail)
                obj_img.save(filename_thumbnail)
                return filename_thumbnail
                
            else:
                obj_img.save(self.file.path)
                self.width=width
                self.height=height
                #return self.file.path
            
        return self.file.path
    def ftp_file_name(self,_dir):
        base, ext = os.path.splitext(os.path.basename(self.file.path))
        if not self.name:
            self.name=base
        filename=_dir+str(self.pk)+ext
        
        self.urls=os.path.join(self.urls,filename)
        self.size=os.path.getsize(self.file.path)
        
        
        thumbnail=_dir+str(self.pk)+'_thumbnail'+ext
        
        _file={}
        _file[filename]=self.scale_dimensions(filename_thumbnail=None)
        _file[thumbnail]=self.scale_dimensions(max_width=300,filename_thumbnail=thumbnail)
        return _file
    def get_thumbnail_img(self):
        thumbnail='_thumbnail'
        
        base, ext = os.path.splitext(self.urls)
        urls_thum='%s%s%s' % (base,thumbnail, ext)
        return "%s/%s/%s" % (self.server.name if self.server else '' ,urls_thum)

    def __unicode__(self):
        return "%s%s" % (self.server.name if self.server else '' ,self.urls)
 
    class Meta:
        # managed = False
        db_table = 'store_img'
        verbose_name = u'图片'
        verbose_name_plural = u'图片'
        app_label='web_site'


class storeParagraph(models.Model):
    #id = models.AutoField(u'id',primary_key=True)
    name = models.CharField(u'标题',max_length=100,blank=True )
    txt =  models.TextField(u'内容',blank=True)
    order=models.IntegerField(verbose_name=u'顺序',default=0,blank=True, )
    create_time = models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
    last_time = models.DateTimeField(auto_now=True,verbose_name=u'最后编辑时间')
    def __unicode__(self):
        return  self.name
    
    
    class Meta:
        # managed = False
        db_table = 'store_paragraph'
        verbose_name = u'文字段落'
        verbose_name_plural = u'文章段落'
        app_label='web_site'


class storeBase(models.Model):
    ct=(
        (0,u''),
        (1,u''),
        (2,u''),      
      )
    title = models.CharField(u'标题',max_length=200,blank=True)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name=u'最后编辑时间')
    edit = models.ForeignKey(User,verbose_name = u'编辑' ,related_name='Base_edit' )
    last_edit = models.ForeignKey(User,verbose_name = u'最后编辑' ,related_name='Base_last_edit')
    
    tag = models.ManyToManyField(storeTag,blank=True, verbose_name=u"标签", related_name='Base_tag' )
    img = models.ManyToManyField(storeImg,blank=True, verbose_name = u"图片",related_name = 'Base_img')
    file = models.ManyToManyField(storeFile,blank=True, verbose_name = u"文件",related_name = 'Base_file')
    paragraph=models.ManyToManyField(storeParagraph,blank=True, verbose_name = u"段落",related_name = 'Base_par')
    order = models.SmallIntegerField(u'排序',default=0)
    state=models.SmallIntegerField(u'状态',choices=ct,default=0)
    level = models.IntegerField(u'等级',default=0)
    def __unicode__(self):
        return '%s' % (self.title)
    class Meta:
        # managed = False
        db_table='store_base'
        app_label='web_site'
