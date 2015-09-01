#coding:utf-8
from django.db import models
from django.contrib.auth.models import User
from base.models import storeImg,storeBase,storeTag
import datetime

class storeCity(models.Model):
    ct=(
        (0,u'无效'),
        (1,u'有效'),
        )
    title = models.CharField(u'城市名称',max_length=50, unique=True)
    code = models.CharField(u'拼音代码',max_length=30, blank=True,unique=True)
    parent = models.ForeignKey('self',  blank=True, related_name='children',verbose_name=u'上一级')

    capital_letter = models.CharField(u'城市首字母',max_length=5)
    usetype = models.IntegerField(blank=True, verbose_name=u'状态',choices=ct,default=1)
    baidu_code = models.IntegerField(u'百度区域代码',blank=True)
    order = models.IntegerField(u'排序',default=0)
    level=models.IntegerField(u'级别',default=0)
    img = models.ManyToManyField(storeImg,blank=True,verbose_name=u'图片',related_name = 'city_img')
    des=models.CharField(u'城市描述',max_length=150, blank=True)

    def __unicode__(self):
        return self.title
    class Meta:
        # managed = False
        db_table = 'store_city'
        verbose_name = u'城市地区'
        verbose_name_plural = u'城市地区' 


class storeCurrency(models.Model):
    name= models.CharField(u'币种',max_length=50,blank=True,unique=True )
    ename= models.CharField(u'币种符号',max_length=10,blank=True,unique=True )
    rate=models.FloatField(u'汇率%',blank=True, null=True )
    sign=models.CharField(u'符号',max_length=50,blank=True, null=True,default=u'￥')
    def __unicode__(self):
        return '%s (%s)' % (self.name,self.rate,)
    class Meta:
        # managed = False
        db_table='store_currency'
        verbose_name = u'币种'
        verbose_name_plural = u'币种'

class storeAddress(storeBase):
    longitude_baidu = models.FloatField(blank=True)
    latitude_baidu = models.FloatField(blank=True)
    longitude_google = models.FloatField(blank=True)
    latitude_google = models.FloatField(blank=True)
    city = models.ForeignKey(storeCity,verbose_name=u'城市',related_name='addr')
    address = models.CharField(u'地址',max_length=400 )
    name = models.CharField(u'名称',max_length=300, blank=True, null=True)
    content=models.CharField(u'地址描述',max_length=500,blank=True,null=True)

    class Meta:
        # managed = False
        db_table='store_address'
        verbose_name = u'地址'
        verbose_name_plural = u'地址'
        
class storeUser(User):
    tag=models.ManyToManyField(storeTag,verbose_name=u"标签" ,related_name='user_tag' )    
    description=models.CharField(u'描述',max_length=500,blank=True)
    photo=models.ManyToManyField(storeImg,verbose_name = u"图片",blank=True)
    user_groups = models.ManyToManyField('self',verbose_name = u'关系',blank=True,related_name = 'fen')
    phone = models.CharField(u'手机',max_length=100,blank = True)
    weixin_code = models.CharField(u'微信代码',max_length=255, blank = True)
    address = models.ManyToManyField(storeAddress,blank = True,verbose_name = u'地址',related_name = 'user_adddress')
    app_user_id=models.IntegerField(u'user_id',blank = True )
    def __unicode__(self):
        return self.username

    class Meta:
        # managed = False
        db_table = 'store_user'
        verbose_name = u'用户'
        verbose_name_plural = u'用户'
class storeProduct(storeBase):
    st=( (0,u'无效'),
          (1,u'有效'), 
          )
    typ=((0, u'标准原价'),
         (1, u'现场交费'),
         (2, u'折扣'),
         (3, u'独家'),
         (4, u'限时'),
         (5, u'闪购'),
         (6, u'反现'),
         )

    price=models.DecimalField(u'售价',max_digits=14, decimal_places=2)
    sale=models.DecimalField(u'折扣价格 ',max_digits=14, decimal_places=2,blank=True )
    discount=models.DecimalField(u'折扣率 ',max_digits=14, decimal_places=2,blank=True )
    original_price=models.DecimalField(u'原价',max_digits=14, decimal_places=2,blank=True )
    currency=models.ForeignKey(storeCurrency, verbose_name=u'货币单位',default=1,related_name='product')
    begin_time = models.DateTimeField( verbose_name=u'开始时间',blank=True ,default=datetime.datetime.now())
    end_time = models.DateTimeField( verbose_name=u'结束时间',blank=True ,default=datetime.datetime.now())
    rel_time = models.DateTimeField( verbose_name=u'发布时间',blank=True ,default=datetime.datetime.now())
    
    stock=models.IntegerField(u'库存',default=100)
    stock_d=models.IntegerField(u'出库等待' ,default=0)
     
    points=models.IntegerField(u'积分',blank=True)
    status = models.PositiveSmallIntegerField(u'有效状态',blank=True ,default=1,choices=st )
    type=models.PositiveSmallIntegerField(u'类型',blank=True, default=0,choices=typ )
    content=models.CharField(u'产品描述',max_length=255,blank=True )
    product_user = models.ManyToManyField(storeUser,verbose_name = u"参与用户",blank=True,related_name='product')

    class Meta:
        # managed = False
        db_table='store_product'
        verbose_name = u'产品'
        verbose_name_plural = u'产品'


class storeEvent(storeBase):
    parent = models.ForeignKey('self',  blank=True, related_name='children',verbose_name=u'上一级')
    content = models.CharField(u'内容',max_length=500)
    address = models.ManyToManyField(storeAddress,verbose_name = u"地址",blank=True)
    product = models.ManyToManyField(storeProduct,verbose_name = u"产品",blank=True,related_name='event')
    event_user = models.ManyToManyField(storeUser,verbose_name = u"参与用户",blank=True,related_name='event')
    
    begin_time = models.DateTimeField( verbose_name=u'开始时间',blank=True ,default=datetime.datetime.now())
    end_time = models.DateTimeField( verbose_name=u'结束时间',blank=True ,default=datetime.datetime.now())
    class Meta:
        # managed = False 
        db_table='store_event'
        verbose_name = u'活动'
        verbose_name_plural = u'活动'


class storeInfo(storeAddress):

    summary = models.CharField(u'简介',max_length=500,blank=True)
    open_date = models.DateField(blank=True,verbose_name=u"开业时间")
    business_hours = models.CharField(blank=True,verbose_name=u"营业时间",max_length=200)
    event = models.ManyToManyField(storeEvent,verbose_name = u"事件",blank=True,related_name='store')
    store_user = models.ManyToManyField(storeUser,verbose_name = u"店员",blank=True,related_name='store')
    product = models.ManyToManyField(storeProduct,verbose_name = u"产品",blank=True,related_name='store')
    groups = models.ManyToManyField('self',verbose_name = u'关系',blank=True,related_name='store')

    class Meta:
        # managed = False 
        db_table='store_info'
        verbose_name = u'店铺'
        verbose_name_plural = u'店铺'

class storeCatType(models.Model):
    name = models.CharField(u'名称',max_length=100)
    templets = models.CharField(u'模板',max_length=100, blank=True)
    def __unicode__(self):
        return self.name
    class Meta:
        # managed = False
        db_table = 'store_cat_type'
        verbose_name = u'分类类型'
        verbose_name_plural = u'分类类型'
        

class storeCat(storeBase):
    city = models.ManyToManyField(storeCity,blank=True,verbose_name=u'城市',related_name='cat_city')
    store = models.ManyToManyField(storeInfo,blank=True,verbose_name=u'店铺',related_name='cat_store')
    event = models.ManyToManyField(storeEvent,blank=True,verbose_name=u'活动',related_name='cat_event')
    product = models.ManyToManyField(storeProduct,blank=True,verbose_name=u'产品',related_name='cat_product')    
    parent = models.ForeignKey('self',  blank=True, related_name='children',verbose_name=u'上一级')
    type = models.ForeignKey(storeCatType,verbose_name=u'类型',blank=True )
    flag = models.CharField(u'标识',max_length=20,blank=True)
    subtitle = models.CharField(u'副标题',max_length=200,blank=True)    
    summary = models.CharField(u'简介',max_length=500,blank=True)
    class Meta:
        db_table = 'store_cat'
        verbose_name = u'分类'
        verbose_name_plural = u'分类'
        
'''
class storeOrder(storeBase):
    order_user = models.ForeignKey(storeUser,verbose_name = u'订单用户',related_name = 'order_user')
    order_code = models.CharField(u'订单号',max_length=255,)
    product = models.ManyToManyField(storeProduct,verbose_name = u'产品',related_name = 'order_product')
    totalpay = models.DecimalField(u'订单总额',max_digits=12, decimal_places=2)    
    address = models.ForeignKey(storeAddress,verbose_name = u'收货地址',related_name = 'order_address')
    discount = models
'''