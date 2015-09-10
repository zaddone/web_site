#coding:utf-8

import urllib2
import json
import re
import random
from django.http import HttpResponse
from django.core.cache import cache
from website.common import getCity,get_site_event,search_sphinx
from website.models import url_page_info


def getPageInfo(key='',new=False):
    keyname = 'PageInfo%s' % (key)
    _list_k = cache.get(keyname)
    if not _list_k or new:
        try:
            page = url_page_info.objects.get(url=key)
        except:
            _list_k = page ={}
        
        if page:
            _list_k = getModelsDict(page)
            
            _link = getattr(_list_k['links'],'order_by',None)('order','id')
            link_list=[]
            for li in _link:
                _li = getModelsDict(li)
                if _li['img']:
                    _li['img']=getattr(_li['img'],'urls',None)
                link_list.append(_li)
            _list_k['links']=link_list
        
        cache.set(keyname ,_list_k,3600)

    return _list_k

def getModelsDict(obj):
    _li = {}
    for i_n in obj._meta.get_all_field_names():
        #if i_n!='links':
        _li[i_n]=getattr(obj, i_n, None)
        #print type(_li[i_n])
    return _li




def get_city_list(ty=0,new=False):
    #type=1 dict(id)
    #type=2 dict(city_name)
    #type=3 dict(Abroad,Domestic)
    id_cache='id'
    name_cache='city_name'
    Abroad_cache='Abroad'
    title = 'title'
    non='None'
    key=non
    if ty==1:
        key=id_cache
    elif ty==2:
        key=name_cache
    elif ty==3:
        key=Abroad_cache
    elif ty == 4:
        key=title
    
        
    #new=True
    _list = cache.get('city_list_a%s' % (key,))
    if not _list or new:
        
        
        city_list= getCity() #sorted(getCity(),key = lambda x:x['parent_id'])   
        id_dict={}
        title_dict={}
        name_dict={}
        Abroad_dict={}
        Abroad_dict['abroad']=[]
        Abroad_dict['domestic']=[]
        for ci in city_list:
            id_dict[ci['id']]=ci
            name_dict[ci['name']]=ci
            title_dict[ci['title'].lower()]=ci
            if ci['parent_id']==106:
                Abroad_dict['abroad'].append(ci)
            else:
                Abroad_dict['domestic'].append(ci)
            
            
        cache.set('city_list_a%s' % (id_cache,), id_dict, 3600*24*30)
        cache.set('city_list_a%s' % (name_cache,), name_dict, 3600*24*30)
        cache.set('city_list_a%s' % (Abroad_cache,), Abroad_dict, 3600*24*30)
        cache.set('city_list_a%s' % (non,), city_list, 3600*24*30)
        cache.set('city_list_a%s' % (title,), title_dict, 3600*24*30)
        if ty==1:
            _list=id_dict
        elif ty==2:
            _list=name_dict
        elif ty==3:
            _list=Abroad_dict
        elif ty == 4:
            _list=title_dict
        else:
            _list=city_list
            
    return _list
                
def get_json_info(json_str):
    return eval(json_str.decode('utf-8').encode('utf-8'), type('Dummy', (dict,), dict(__getitem__=lambda s,n:n))())


def getCityNameByCity(request):
    
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip =  request.META['HTTP_X_FORWARDED_FOR']
        ip = ip.split(",")[0]
    else:
    
        ip = request.META['REMOTE_ADDR']
    #print 'ip=',ip
    locApiUrl = 'http://apis.baidu.com/apistore/iplookupservice/iplookup?ip=%s'%ip    
    req=urllib2.Request(locApiUrl)
    req.add_header('Content-Type', 'text/html; charset=utf-8')    
    req.add_header('apikey', '7041fb9f4922e5b76465d132da83bab6')
    
    
    try:
        rp = urllib2.urlopen(req,timeout=5).read()
        #jsondic = get_json_info(rp)
        #return jsondic
        jsondic = json.loads(rp)
        return jsondic
        content = jsondic.get('retData',False)
        if content:
            city = content.get('city',False)
            if city:
                return city
        return {'ip':ip}
    except:
        return {'ip':ip}


def return_get_arr(url='/',nowCity=[],query=None):
    if query:
        get_arr =  request_val(query)
        if 'page' not in get_arr:
            get_arr['page']=1

        return get_arr
    arr_url= url.split('?')
    get_arr={}
    if len(arr_url)==2:
        
        for val in arr_url[1].split('&'):
            val=val.split("=")
            get_arr[val[0]]=val[1]
            #arr.append({'key':'','val'})
    if nowCity and 'cityid' not in get_arr:
        get_arr['cityid']=','.join(nowCity)
    if 'page' not in get_arr:
        get_arr['page']=1
    else:
        get_arr['page']=int(get_arr['page'])
    return get_arr


def request_val(_str=''):
    # city is first pinyin string  other value is int in _str
    array={'t':'tag','c':'cat','p':'page','l':'perpage'}
    req={}
    city_re=re.compile(r'[a-z]+(?!\d)')
    date_re=re.compile(r'(\d+){6,8}')
    
    d=date_re.findall(_str)
    if len(d)>0:
        req['date']=d
    m = city_re.findall(_str)
    if len(m)>0:
        req['city']=m
        
    other=re.compile(r'([a-z]\d+)')
    o=other.findall(_str)
    for i in o:
        if array[i[0]] not in req:
            req[array[i[0]]]=[]
        req[array[i[0]]].append(int(i[1:]))
 
    return req

def get_url_str(get_arr,page=None,request_str='/'):
    _get_url=[]
    array={'tag':'t','cat':'c','page':'p','perpage':'l'}
    for k in get_arr:
        if k == 'city':
            for ci in get_arr[k]:
                if ci != 'list':
                    _get_url.append(ci)
        elif page>1 and k=='page':
            _get_url.append('%s%s' % (array[k],page))
        elif k=='date':
            for da in get_arr[k]:
                _get_url.append(da)
        elif type(get_arr[k])==list:
            for ids in get_arr[k]:
                _get_url.append('%s%s' % (array[k],ids))
        
        elif k in array and k!='page' and k!='date':
            _get_url.append('%s%s' % (array[k],get_arr[k]))

        
    if _get_url:
        return request_str +'_'.join(_get_url)+'/'
    else:
        return request_str
        
def get_url(request,get_arr,page=None,query=None):
    if query:
        return  get_url_str(get_arr,page)
        

    _get_url=''

    for k in get_arr:
        if  _get_url:            
            _get_url+='&'
        if page and k=='page':
            _get_url+='%s=%s' % (k,page)
        else:
            _get_url+='%s=%s' % (k,get_arr[k])
    
    return '%s?%s' % (request.path,_get_url)
def pagination(request,count,perpage,pageNum=10,nowCity=[],query=None):
    page=[]
    get_arr=return_get_arr(request.get_full_path(),nowCity,query=query)
    page_count=count/perpage
    if count%perpage:
        page_count+=1
    '''
    if pageNum>page_count:
        pageNum=page_count
    '''
    
    Node=pageNum/2+pageNum%2
    
    
    if type(get_arr['page'])==list:
        get_arr['page']=int(get_arr['page'][0])
    k=int(get_arr['page'])+Node
    
    if k > pageNum:
        end=k
        begin = k-pageNum
        if k>page_count:
            begin -=k-page_count
            
        if begin<1:
            begin=1
        
        if begin>1:
            page.append({'name' : u'首页','url':get_url(request,get_arr,1,query=query),'flg':False})
        #page.append({'name' : u'上一页','url':get_url(request,get_arr,get_arr['page']-1),'flg':False})
    else:
        end= pageNum+1
        begin=1
    if get_arr['page']>1:
        page.append({'name' : u'上一页','url':get_url(request,get_arr,get_arr['page']-1,query=query),'flg':False})
    for i in range(begin,end):        
        if i>page_count:
            break
        flg=False
        if int(get_arr['page'])==i:
            flg=True
        page.append({'name' : i,'url':get_url(request,get_arr,i,query=query),'flg':flg})

    if get_arr['page']<page_count:
        page.append({'name' : u'下一页','url':get_url(request,get_arr,get_arr['page']+1,query=query),'flg':False})
    if k<page_count:
        page.append({'name' : u'尾页','url':get_url(request,get_arr,page_count,query=query),'flg':False})
    
    if len(page)==1:
        return []
    return page

def return_callback_http(callback,data):
    if callback:
            re='%s(%s);' % (callback,json.dumps(data,separators=(',',':')))
            Http = HttpResponse( re)
    else:
        re=json.dumps(data)
        Http = HttpResponse( re, content_type="application/json")
    return Http


def find_search_id(ev_id=None, city_name = None, tags=None, indexer='*',):
    kw = '@cities "%s" @tags "%s"/1' %(city_name, tags)
    ids = search_sphinx(kw, indexer=indexer, limits=10)
    return ids
def recommend( ev_id=None, city_name = None, tags=None, new=False, indexer='*',number=2):
        '''
        猜你喜欢
        '''
        ids = find_search_id(ev_id,city_name,tags,indexer)

        random.shuffle(ids)

        more = []
        n = 0
        for i in ids:
            if i == ev_id:
                continue 
            e = get_site_event(event_id = i,detail=False,new=new)
            
            if e:
                more.append(e)
            n += 1
            if n == number:
                break

        return more

