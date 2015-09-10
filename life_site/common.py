#coding:utf-8
import re
import json
from datetime import date,timedelta, datetime
from django.db.models import Q
from django.core.cache import cache
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from BeautifulSoup import BeautifulSoup
from LifeApi.models import NewEventCat,feelnum,CityTheme,NewDistrict
from LifeApi.common import NewAppEvent

from website import sphinxapi


def get_one_data(data=date.today(),new=False):
    date_str = datetime.datetime.strftime(date, '%Y-%m-%d')
    showtime_dict = cache.get(date_str)
    if not showtime_dict and new:        
        fe = feelnum.objects.filter(showtime =date.today())\
            .exclude(showtime=None).order_by('-feelnum','id')
        
    pass

def get_time_line(dict_type=0,city_id=None,new=False):
    key_showtime_dict = 'showtime_dict%s' % (city_id if city_id else 'all')
    key_showtime_list = 'showtime_list%s' % (city_id if city_id else 'all')
    key_showtime_Week = 'showtime_Week%s' % (city_id if city_id else 'all')
    
    if not new:
        if dict_type == 0:
            showtime_dict = cache.get(key_showtime_dict)
            if not showtime_dict:
                new=True
        elif dict_type == 1:
            showtime_list = cache.get(key_showtime_list)
            if not showtime_list:
                new=True
        elif dict_type == 2:
            showtime_Week = cache.get(key_showtime_Week)
            if not showtime_Week:
                new=True
    
    
    if new:
        showtime_list=[]
        showtime_dict={}
        showtime_Week=[]
        fe = feelnum.objects.filter(showtime__lte=date.today())\
                .exclude(showtime=None).order_by('-showtime','-feelnum') 
        
        if city_id:
            fe=fe.filter(event__city=int(city_id))
        
        showdate=''
        one_week=None
        week=[]
        
        for f in fe:

            f_list={}
            f_list['date'] = datetime.strftime(f.showtime,'%Y-%m-%d')
            f_list['id']=f.event.id
            f_list['title'] = f.event.fname if f.event.fname else f.event.name
            f_list['daytitle'] = f.title
            f_list['img'] = []
            for imgs in f.event.img.exclude(order=9999).order_by('-order','-id'):        
                if imgs.server:
                    f_list['img'].append(imgs.server.name+imgs.urls)
                else:
                    if re.match('/',imgs.urls):
                        f_list['img'].append('http://pic.huodongjia.com'+imgs.urls)
                         
                    else:
                        f_list['img'].append('http://pic.huodongjia.com/'+imgs.urls)
            
            #f_list['city']=[ ci.id  for ci in f.event.city.all()]
            
            if not showtime_dict.has_key(f_list['date']):
                showtime_dict[f_list['date']]=[]
                showtime_list.append(f_list['date'])
                if showdate:                    
                    week.append(f_list['date'])
                
                if not one_week or one_week>f.showtime:
                    we= f.showtime.weekday()
                    if we==0:
                        we=7
                    one_week=f.showtime+timedelta(days=-(we-1))
                    if week:
                        showtime_Week.append(week[:])                    
                        week=[]
                        
                
                
                
                    
            showtime_dict[f_list['date']].append(f_list)
            
            showdate=f_list['date']
        
        cache.set(key_showtime_dict,showtime_dict,3600*12)
        cache.set(key_showtime_list,showtime_list,3600*12)
    
    else:
        pass
    
    if dict_type==0:
        return showtime_dict
    elif  dict_type==1:
        return showtime_list
    elif  dict_type==2:
        if len(week)>0:
            showtime_Week.append(week[:]) 
        return showtime_Week


def getCity(id_list=[]):
    if id_list:
        citys = NewDistrict.objects.filter(id__in=id_list)
    else:
        citys = NewDistrict.objects.exclude(img__isnull=True).order_by('-event_count')
    ca=[]
    # cc={}
    for city in citys:
        cct={}
        cct['id']=city.id
        cct['name']=city.district_name
        cct['des']=city.des if city.des else ''
        cct['title']=city.title

        
        try:
            if city.img:
                
                imgs=city.img

                if imgs.server:
                    cct['img'] = imgs.server.name+imgs.urls
                else:
                    if re.match('/',imgs.urls):
                        cct['img']='http://pic.huodongjia.com'+imgs.urls
                    else:
                        cct['img']='http://pic.huodongjia.com/'+imgs.urls

        except:
            
            cct['img']=''
        if city.parent:
            cct['parent_name']=city.parent.district_name
            cct['parent_id']=city.parent.id

        ca.append(cct)
  
    return ca


def format_event_from_app(res={},detail=False):
    if not res:
        return {}
    ev={}
    ev['id']=res['event_id']
    ev['title'] = res['title']
    ev['tag'] = res['event_tag_id'] if 'event_tag_id' in res else res['event_tag']
    ev['address'] = res['event_address']
    ev['venue'] = res['event_venue']
    ev['city_id'] = res['district_id'] 
    ev['city_title'] = res['district_title'] 
    ev['city_name'] = res['district_name'] 

    ev['imgs'] =[]# res['img_s']
    for img in res['img_s']:
        ev['imgs'].append(replace_img(img))
    
    if detail:
        ev['detail'] = res['detail'] if 'detail' in res and res['detail'] else res['des']
        ev['content']=[]
        for da in res['event_content']:
            txt = add_img_alt(da[1],ev['venue'])
            ev['content'].append((da[0],txt))

        
    #event['more']=self.more(event['id'], ca['district_id'], new)
    
    
    return ev


def add_img_alt(text,val):
    text = BeautifulSoup(text)
    
    for _img in text.findAll('img'):           
    
        if _img.has_key('alt'):
            if not _img['alt']:
                _img['alt']=val
        else:
            _img['alt']=val
            
        if _img.has_key('title'):
            if not _img['title']:
                _img['title']=val
        else:
            _img['title']=val
            
        if _img.has_key('src'):
            _img['src']=replace_img(_img['src'])
            
    return str(text).strip()

def replace_img(_val):
    _val=_val.replace('pic.huodongjia.com','img1.xiaorizi.me').replace('pic1.qkan.com','img1.xiaorizi.me')
    return _val
def get_site_event(event_id,detail=False,new=False):
    '''
    get format data to  web page 
    '''
    new=1
    keyname = 'event_site_%s_%s' % (event_id,detail)
    res  = cache.get(keyname) 
    if not res or new:
        
        # move data ....
        res = format_event_from_app(NewAppEvent(None,event_id,new),detail)
        if res:

            cache.set(keyname,res , 86400*30)
    return res

def search_sphinx(kw, indexer='*', limits=100):
    '''
    通过sphinx进行搜索，indexer对应sphinx配置
    采用extended matching mode
    详见：http://sphinxsearch.com/docs/current/extended-syntax.html
    '''
    if not kw:
        return []
    
    cl = sphinxapi.SphinxClient()
    cl.SetServer('10.10.43.180',9313)
    cl.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
    cl.SetLimits(0,limits)
    res = cl.Query(kw, indexer) 

    if res and 'matches' in res:
        return [match['id'] for match in res['matches']]
    else:
        return []
def get_cat_tag(typeid = 6,new=False,ty = 0):
    
    id_cache='id'
    name_cache='city_name'
    non='None'
    key=non
    if ty==1:
        key=id_cache
    elif ty==2:
        key=name_cache

    
    if not typeid:
        return []
    keyname = 'get_cat_tag_%s_%s' % (typeid,key)
    _list_k = cache.get(keyname)
    if not _list_k or new:
        _list=[]
        _id_dict={}
        _name_dict={}
        
        _name_dict['cat_name_dict']={}
        _name_dict['tag_name_dict']={}
        
        _id_dict['cat_id_dict']={}
        _id_dict['tag_id_dict']={}
        cats = NewEventCat.objects.filter(type_id=typeid)
        fns = feelnum.objects.filter(event__isshow_id=1).\
                filter(Q(event__end_time__gt=date.today())|Q(event__end_time=None)).\
                order_by('-event__rel_time')
        _fn_ids = []
        for cat in cats.all():
            _dict = {
                    'id': cat.id,
                    'title': cat.name,
                    'tags': [],
                    }
            _name_dict['cat_name_dict'][cat.name]=_dict
            _id_dict['cat_id_dict'][cat.id]=_dict
            for tag in cat.tag.all():
                _tag_dict = {
                        'id': tag.id,
                        'name': tag.name,
                        'img': '',
                        'ev_count': 0,
                        }
                
                try:
                    _fns = fns.filter(event__tag=tag)
                    if cat.id == 234:
                        # 探店
                        _fns = _fns.filter(event__shoporevent=1)

                    elif cat.id == 235:
                        # 活动
                        _fns = _fns.filter(event__shoporevent=2)

                    _tag_dict['ev_count'] = len(_fns)
                    if _tag_dict['ev_count'] < 1:
                        continue
                    _tag_dict['img'] = img_repeat_handle(_fn_ids, _fns)

                except IndexError:
                    continue

                _name_dict['tag_name_dict'][tag.name]=_dict
                _id_dict['tag_id_dict'][tag.id]=_tag_dict
                _dict['tags'].append(_tag_dict)
            if _dict['tags']:
                _list.append(_dict)
        cache.set('get_cat_tag_%s_%s' % (typeid,non), _list, 3600*24*30)          
        cache.set('get_cat_tag_%s_%s' % (typeid,id_cache), _id_dict, 3600*24*30)    
        cache.set('get_cat_tag_%s_%s' % (typeid,name_cache), _name_dict, 3600*24*30)    
        _list_k=_list
        if ty==1:
            _list_k=_id_dict
            
        elif ty==2:
            _list_k=_name_dict
            
         
    return _list_k
def get_img_url(img_obj):
    if img_obj.server:
        return img_obj.server.name + img_obj.urls
    else:
        if img_obj.urls.startswith('/'):
            return 'http://pic.huodongjia.com' + img_obj.urls
        else:
            return 'http://pic.huodongjia.com/' + img_obj.urls

def img_repeat_handle(ids, event_list):
    evs = event_list.exclude(id__in=ids)
    if not evs:
        evs = event_list
    ev = evs[0]
    imgs = ev.event.img.order_by('-order', '-id')
    if imgs:
        ids.append(ev.id)
        return get_img_url(imgs[0])
       

def get_tag_event(tagid=None,cityid=None,catid=None,page=1,perpage=20,new=False):
    
    
    if perpage:
        keyname = 'tag_home_%s_%s_%s_%s_%s' % (tagid,cityid,catid,page,perpage)
    else:
        keyname = 'tag_home_%s_%s_%s' % (tagid,cityid,catid)
    _list = cache.get(keyname)
    #new=True
    if not _list or new:
        
        
        fns = feelnum.objects.filter(event__isshow_id=1).filter(Q(event__end_time__gt=date.today())|Q(event__end_time=None)).order_by('-showtime','-event__rel_time')
        fns = fns.filter(showtime__lte=date.today())
        if cityid:
            cityid = cityid.split(',')
            if '0' not in  cityid:
                fns=fns.filter(event__city__in=cityid)

        if catid:
            catid = catid.split(',')
            fns=fns.filter(event__tag__in=catid)
        if tagid:
            tagid = tagid.split(',')
            fns=fns.filter(event__tag__in=tagid)
        
        if perpage:
            (start,end)=getListStartToEnd(page,perpage)
            _list = [fn.event.id for fn in fns[start:end]]
        else:
            _list = fns.count()
        cache.set(keyname, _list, 3600*2)
        
    return _list
def getListStartToEnd(page,offset):
    if not page:
        page=1
    if not offset:
        offset=20
    start = (page-1)*offset
    end = page*offset        
    return (start,end)

def get_theme_db(cityid=None):
    theme = CityTheme.objects.filter(Q(end_time=None) | Q(end_time__gt=date.today()))   
    #Editr after date for 2015-6-15 not show 
    theme = theme.filter(begin_time__gt=date(2015,6,15))  
    if cityid:     
        theme = theme.filter(city=cityid).distinct()
        
    return [th.id for th in theme]

def theme_page(request):
    cds = request.GET
    themeid = cds.get('themeid')
    new = cds.get('new')
    keyname = 'xrz_themeid_%s' %themeid

    var = cache.get(keyname)

    if not var or new:
        var = {}
        if themeid:
            try:
                theme = CityTheme.objects.get(id=themeid)
            except ObjectDoesNotExist:
                var['msg'] = 'invalid themeid'
                var['code'] = 0
                return HttpResponse(json.dumps(var), content_type='application/json')
        else:
            var['msg'] = 'need themeid'
            var['code'] = 0
            return HttpResponse(json.dumps(var), content_type='application/json')

        var['theme_title'] = theme.name
        var['theme_img'] = get_img_url(theme.img)

        var['theme_intro'] = theme.intro
        var['theme_keywords'] = theme.keywords

        var['shops'] = []

        remove_vtline = lambda text: text[text.find('|')+1:].lstrip()

        for fe in feelnum.objects.filter(event__theme__in=(themeid,), 
                        event__isshow_id=1).order_by('-feelnum', '-event__end_time'):
            ev = fe.event
            _tmp = {}
            _tmp['name'] = remove_vtline(ev.name)
            _tmp['intro'] = ev.content.replace('\r', '').replace('\n', '')
            try:
                _addr = ev.addr.all()[0]
                _tmp['address'] = _addr.address if _addr.address else ''
                _tmp['addresstitle'] = _addr.title if _addr.title else ''
            except IndexError:
                _tmp['address'] = ''
                _tmp['addrtitle'] = ''
            try:
                _tmp['img'] = get_img_url(ev.img.order_by('-order', '-id')[0])
            except IndexError:
                _tmp['img'] = ''
            var['shops'].append(_tmp)
        
        cache.set(keyname, var, 3600)
    template_name = 'themepage.html'

    return render(request, template_name, var)

