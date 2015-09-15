#coding:utf-8
import time
import datetime
from django.http import HttpResponse,Http404
from django.utils import simplejson as json
from django.template import RequestContext
from django.shortcuts import render_to_response

from website.common import get_cat_tag,get_tag_event,get_time_line,theme_page,get_one_data

from website.functions import getCityNameByCity,get_city_list,pagination,\
                request_val,get_url_str,return_callback_http,getPageInfo,get_site_event,\
                recommend


re_key={'domestic':{"name":u"国内","title": "domestic"},
        'abroad':{"name":u"国外","title": "abroad"},
        'list':{"name":u"全国","title": "list"},
       }

def site_theme_page(request):
    return theme_page(request)


def get_request_city_val(arr,new=None,re_key=None):
    now_city=[]
    if arr and 'city' in arr:
        #arr = request_val(query)
        ci_title = get_city_list(4,new)
        if ci_title:
            now_city=[]
            for ci in arr['city']:                    
                
                if re_key and ci in re_key:
                    if ci == 'list':
                        now_city=['0']
                        break
                    else:                            
                        db_city=get_city_list(3,new)
                        for cit in db_city[ci]:
                            now_city.append(str(cit['id']))
                        break
                if ci in ci_title:
                    now_city.append(str(ci_title[ci]['id']))
    return now_city
def get_request_cat_val(arr,new=None,tag=False,):
    now_cat = []
    cat_id_list=get_cat_tag(new=new,ty=1)
    if arr.has_key('cat') and cat_id_list.has_key('cat_id_dict'):            
        for cat in arr['cat']:
            if cat in cat_id_list['cat_id_dict']:
                now_cat.append(str(cat))

    if tag and arr.has_key('tag') and  cat_id_list.has_key('tag_id_dict') :
        now_tag=[]
        for ta in arr['tag']:
            if ta in cat_id_list['tag_id_dict']:
                now_tag.append(str(ta))

        return (now_tag,now_tag)
    return now_cat

def get_request_val(request,arr=None,new=None,re_key=None):
    now_tag = [ str(ta) for ta in arr['tag'] ] if 'tag' in arr else []
    now_cat = get_request_cat_val(arr=arr,new=new)
    now_city= get_request_city_val(arr=arr,new=new,re_key=re_key)
    if arr:   
        
        if arr.has_key('page'):
            page = arr['page'][0]
        else:
            page =1
            
        if arr.has_key('perpage'):
            perpage = arr['perpage'][0]
        else:
            perpage =18
    else:     
        page = int(request.GET.get('page',1))
        perpage =   int(request.GET.get('perpage',15))
        
    city_id=request.GET.get('cityid',[])
    cat_id=request.GET.get('catid',[])
    tag_id=request.GET.get('tagid',[])

    if city_id:
        city_id=city_id.split(',')
    if now_city:
        city_id.extend(now_city)

        
    if tag_id:
        tag_id=tag_id.split(',')
    if now_tag:
        tag_id.extend(now_tag)
        
    if cat_id:
        cat_id=cat_id.split(',')
    if now_cat:
        cat_id.extend(now_cat)

 
    
    if not city_id and (cat_id or tag_id or page):
        city_id=[0]
    return (city_id,cat_id,tag_id,page,perpage)


def html_return_city(new,cat_id,tag_id,citys={},request_str='/'):
    city_list=get_city_list(ty=3,new=new)
    city_list_new={}
    for city_key in city_list:
        city_list_new[city_key]=[]
        for city in city_list[city_key]:
            item={}
            if cat_id:
                item['cat']=cat_id
            if tag_id:
                item['tag']=tag_id
            item['city']=[city['title']]
            city['url']=get_url_str(get_arr=item,page=None,request_str=request_str)
            if city['title'] in citys:
                city['cur']=True
            city_list_new[city_key].append(city)
            
    return city_list_new
def html_return_cat(new,city_id,cat_id,tag_id):
    cat = get_cat_tag(new=new)
    #city_cache_id = get_city_list(ty=1,new=new)
    city_py=[]
    if city_id:
        for ci in city_id:
            if ci['title'] != 'list':
                city_py.append(ci['title'])

    new_cat=[]
    
    
    for ca in cat:
        ca['url']=get_url_str({'city':city_py,'cat':[str(ca['id'])]})
        if cat_id and str(ca['id']) in cat_id:
            ca['cur']=True
        for tag in ca['tags']:
            tag['url']=get_url_str({'city':city_py,'tag':[str(tag['id'])]})
            if tag_id and str(tag['id']) in tag_id:
                tag['cur']=True
        new_cat.append(ca)
    return new_cat
def get_current_city(city_id=[],new=False,city_key={},query_arr={}):
    data={}
    data['Current_city']=[]
    data['cities']=False
    
    if 'city' in query_arr:
        city_title=get_city_list(ty=4,new=new)  
        for ci in query_arr['city']:
            
            if ci in city_key:
                data['cities']=True
                data['Current_city'].append(city_key[ci])
            elif ci in city_title:
                data['Current_city'].append(city_title[ci])
    if not data['Current_city'] and city_id :      
        #citys=city_id.split(',')
        city_ids=get_city_list(ty=1,new=new)       
        
        for ci in city_id:
            if int(ci)==0:
                data['cities']=True
                data['Current_city'].append(city_key['list'])
                break
            if int(ci) in city_ids:            
                data['Current_city'].append(city_ids[int(ci)])
    if len(data['Current_city'])>1:
        data['cities']=True

    return data

def get_current_cat_and_tag(cat_id,tag_id,new=False):
    data={}
    data['Current_cat']=[]
    data['Current_tag']=[]
    if tag_id or cat_id:
        #br=False
        cat_id_list=get_cat_tag(new=new,ty=1)        
        if cat_id:
            
            for ca in cat_id:
                data['Current_cat'].append(cat_id_list['cat_id_dict'][int(ca)])
                
            if not data['Current_cat']:
                    return False

        if tag_id:
            for ta in tag_id:
                try:
                    tag_dict=cat_id_list['tag_id_dict'][int(ta)]
                    data['Current_tag'].append(tag_dict)
                    if 'cat' in tag_dict:
                        try:
                            cat_dict=cat_id_list['cat_id_dict'][int(tag_dict['cat'])]
                            if data['Current_cat']:
                                try:
                                    data['Current_cat'].index(cat_dict)
                                except:
                                    data['Current_cat'].append(cat_dict)
                            else:
                                data['Current_cat'].append(cat_dict)
                        except:
                            pass
                         
                except:
                    pass
                

            '''
            if not data['Current_tag']:
                return False
            '''
    return data

def life_list_new(request,query=None):
    '''
    Get list page bady data 
    '''
    new=request.GET.get('new',False)
    data={}
    query = query.lower() if query else 'list'
    #data['arr'] = request_val(query)

    data['Current_city']=[]
    data['Current_cat']=[]
    data['Current_tag']=[]
    
    #data['city_key']=re_key
    
    #data['city'] = get_city_list(ty=0,new=new)
    #data['city_list']=get_city_list(ty=3,new=new)
    
    query_arr = request_val(query)
    '''
    if len(query_arr)==1 and 'tag' in query_arr:
        (city_id,cat_id,tag_id,data['Current_page'],data['Current_perpage'])=('0',None,str(query_arr['tag'][0]),1,15)
    else:
    '''
    
    (city_id,cat_id,tag_id,data['Current_page'],data['Current_perpage']) = get_request_val(request,query_arr,new,re_key)
    da = get_current_cat_and_tag(cat_id,tag_id,new)
    if not da:
        return data
    data.update(da)
    data.update(get_current_city(city_id = city_id,new=new,city_key=re_key,query_arr=query_arr))

    if not data['Current_city']:
        return data
    data['Current_city_dict']={}
    for ci in data['Current_city']:
        data['Current_city_dict'][ci['title']]=ci
    
    data['city_list']=html_return_city(new=new,cat_id=cat_id,tag_id=tag_id,citys=data['Current_city_dict'])
    
    data['cat'] = html_return_cat(new=new,city_id=data['Current_city'],cat_id=cat_id,tag_id=tag_id)
    #city_id=None
    if data['Current_cat'] and not data['Current_tag']:
        for _cat in data['Current_cat']:
            for _tag in _cat['tags']:
                tag_id.append(str(_tag['id']))
    if not cat_id:
        cat_id=[]
    data['Current_page_count'] = 0
    event_id_list_count =data['count'] = get_tag_event(tagid=tag_id,catid=cat_id,cityid=city_id,new=new,perpage=None)
    if not event_id_list_count or  event_id_list_count < data['Current_page']:
        return data
    data['Current_page_count'] = event_id_list_count/data['Current_perpage']+1 if event_id_list_count%data['Current_perpage'] else 0
    data['pagination']=pagination(request,event_id_list_count,data['Current_perpage'],pageNum=5,nowCity=city_id,query=query )
    event_id_list = get_tag_event(tagid=tag_id,catid=cat_id,cityid=city_id,page=data['Current_page'],perpage=data['Current_perpage'],new=new)
    data['list']=  [get_site_event(event_id=ev_id,new=new) for ev_id in event_id_list]
    return data
def tag_city_page(request,query=None,template_name='showlist.html'):
    data = life_list_new(request,query)
    '''
    if not data:
        return Http404
    '''
    #return HttpResponse(json.dumps(var), content_type='application/json')
    if request.GET.get('json',False):
        return return_callback_http(request.GET.get("callback",None),data)
        #return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        
        return render_to_response(template_name,data,context_instance=RequestContext(request))


def tag_home_page(request,template_name='showlist.html'):
    

    data = life_list_new(request)
    if not data:
        return Http404
    #return HttpResponse(json.dumps(var), content_type='application/json')
    if request.GET.get('json',False):
        return return_callback_http(request.GET.get("callback",None),data)
        #return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        
        return render_to_response(template_name,data,context_instance=RequestContext(request))


def get_hot_tag():
    tag=[{'name':u'甜品店','url':'/t7291/'},
         {'name':u'书吧 ','url':'/t7182/'},
         {'name':u'餐吧','url':'/t7236/'},
         {'name':u'工作室','url':'/t7368/'},
         {'name':u'面包房','url':'/t7328/'},
         {'name':u'花房','url':'/t7279/'},
         {'name':u'文化空间','url':'/t7402/'},
         ]
    return tag

def life_page(request,query=None,template_name='showpage.html'):

    new=request.GET.get('new',None)
    data = get_site_event(event_id = int(query),detail=True,new=new)

    
    
    data['ad']=request.GET.get('ad',False)
    data['hot_tag']=get_hot_tag()
    if data:
        def get_tag_str(_tag=data['tag']):
            arr={}
            arr['tags']=[]
            arr['more_url']=[]
            arr['tag']=[]
            for tag in _tag:
                if type(tag)==tuple:
                    arr['tags'].append(tag[1])
                    url='t%s' % tag[0]
                    arr['tag'].append(('/%s/' % url,tag[1]))
                    arr['more_url'].append(url)
                else:
                    arr['tags'] ='%s%s' %( arr['tags'],tag)
            if 'more_url' in arr:
                arr['more_url']='/%s/' % ('_').join(arr['more_url'])   
            return arr
        data.update(get_tag_str())
    if 'tags' in data:
        _tags=''.join(data['tags'])
        data['tags']=','.join(data['tags'])
    data['more']= recommend(data['id'], data['city_name'], tags =_tags, new=new )
    data['more_url'] ='/%s/' % data['city_title']
        
    #return HttpResponse(json.dumps(var), content_type='application/json')
    if request.GET.get('json',False):
        return return_callback_http(request.GET.get("callback",None),data)
        #return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        if request.GET.get('share',False):
            template_name='showpage_share.html'
        return render_to_response(template_name,data,context_instance=RequestContext(request))


def find_first_data(date,order=None,fe_dict={},fe_list=[],number=0,recursive=True):
    if number>9:
        return None
    date_str = datetime.datetime.strftime(date, '%Y-%m-%d')
    if date_str in fe_dict:
        #return fe_dict[date_str]
        return fe_list.index(date_str)
        #return fe0[date_str]
    else:
        if not recursive:
            return None
        #return 'not find'
        oneday = datetime.timedelta(days=1)
        if order:
            date=date-oneday
        else:
            date=date+oneday
        number+=1
        return find_first_data(date,order,fe_dict,fe_list,number)

def get_date_list(first_id,day,orders,fe1):
    _list=[]
    if day==1:
        _list.append(fe1[first_id])
    else:

        if orders:
            if not first_id:
                first_id = 0
                
            end=first_id+day
    
            _list=fe1[first_id:end]
        else:
            if not first_id:
                first_id = 1
                
            begin = first_id-day+1
            if begin<0:
                begin = 0
            _list=fe1[begin :first_id]
    return _list


def life_oneday(request,query=None,template_name='showchoice.html'):
    p={}
    p['code']=1
    p['msg']='Request is successful'
    cds = request.GET
    new = cds.get('new',None)
    date = cds.get('date',None)
    day = int(cds.get('day',1))
    orders = 0 if cds.get('order',1)=='0' else cds.get('order',1)
    #Handle city Parameter
    cityid = cds.get('cityid',[])

    
    if query:
        query = query.lower() 
        query_arr = request_val(query)
        if 'city' in query_arr and 'list' not in query:
            day=9
    else:
        query = 'list'
        query_arr = request_val(query)
        
    p['query_arr']=query_arr
    #p['city_list'] = html_return_city(new=new,cat_id=None,tag_id=None,request_str='/choice/')
    p['Current_city']=[] 
    #p['he']=get_current_city(city_id = cityid,new=new,city_key=re_key,query_arr=query_arr)
    p.update(get_current_city(city_id = cityid,new=new,city_key=re_key,query_arr=query_arr))

    if not p['Current_city']:
        return p
    
    p['Current_city_dict']={}
    for ci in p['Current_city']:
        p['Current_city_dict'][ci['title']]=ci
    
    p['city_list']=html_return_city(new=new,cat_id=None,tag_id=None,citys=p['Current_city_dict'])
    newcity = get_request_city_val(arr=query_arr,new=new,re_key=re_key)

    if cityid:
        cityid=cityid.split(',')
    cityid.extend(newcity)
    
    #Handle date Parameter
    new_date=[]
    if not date and 'date' not in query_arr:
        date=datetime.date.today()
        new_date.append(date)
    else:
        if 'date' in query_arr:
            for time in query_arr['date']:
                
                new_date.append(datetime.datetime.strptime( time, "%Y%m%d").date())
        if date:
            try:
                new_date.append(datetime.datetime.strptime( date, "%Y%m%d").date())
            except:
                pass
            
    if len(new_date)==1:
        firstDay=new_date[0]
        oneday = datetime.timedelta(days=1)
        for i in range(int(day)-1):
            
            if orders:
                firstDay = firstDay-oneday
            else:
                firstDay = firstDay+oneday
            
            new_date.append(firstDay)
    p['date_dict']=[]
    p['list']=[]
    p['new_date']=[]
    p['id_list']=[]
    
    for one_day in new_date:
        date_str = datetime.datetime.strftime(one_day, '%Y%m%d')
        p['new_date'].append(date_str)
        id_list=get_one_data(_date =one_day, city_id=cityid,new=new)
        #p['id_list']=id_list
        if id_list:
            for _id in id_list:
                p['list'].append(get_site_event(event_id = _id,detail=False,new=new))
            p['date_dict'].append({date_str:id_list})
    if request.GET.get('json',False):        
        return return_callback_http(request.GET.get("callback",None),p)
        #return HttpResponse(json.dumps(p), content_type='application/json')
    else:        
        return render_to_response(template_name,p,context_instance=RequestContext(request))

def life_choice(request,query=None,template_name='showchoice.html'):
    
    p={}
    p['code']=1
    p['msg']='Request is successful'

    cds = request.GET
    cityid = cds.get('cityid',[])

    date = cds.get('date',None)
    day = int(cds.get('day',1))
    if query:
        query = query.lower() 
        query_arr = request_val(query)
        if 'city' in query_arr:
            day=9
    else:
        query = 'list'
        query_arr = request_val(query)
    
    #p['query']=query_arr
    orders = 0 if cds.get('order',1)=='0' else cds.get('order',1)
    new = cds.get('new',1)
    #Handle city Parameter
    
    newcity = get_request_city_val(arr=query_arr,new=new,re_key=re_key)

    if cityid:
        cityid=cityid.split(',')
    cityid.extend(newcity)

    p['city_list'] = html_return_city(new=new,cat_id=None,tag_id=None,request_str='/choice/')    
    p['Current_city']=[]   
    p.update(get_current_city(city_id = None,new=new,city_key=re_key,query_arr=query_arr))
    if not p['Current_city']:
        return p
    
    fe1 = get_time_line(1, city_id = cityid, new = new)
    fe0 = get_time_line(0, city_id = cityid, new = new)
    p['date_list']=fe1
    p['Current_date']=[]
    
    #Handle date Parameter
    new_date=[]
    if not date and 'date' not in query_arr:
        date=datetime.date.today()
        new_date.append(date)
    else:
        if 'date' in query_arr:
            for time in query_arr['date']:
                new_date.append(datetime.datetime.strptime( time, "%Y%m%d").date())
        if date:
            try:
                new_date.append(datetime.datetime.strptime( date, "%Y%m%d").date())
            except:
                pass
            
    #get data list
    if len(new_date)>1 and day==1:
        for _da in new_date:    
            first_id = find_first_data(_da,orders,fe0,fe1,False)
            if first_id>=0:
                p['Current_date'].append(get_date_list(first_id,day,orders,fe1))  
    elif len(new_date)==1:
        _da=new_date[0]
        first_id = find_first_data(_da,orders,fe0,fe1)
        if first_id>=0:
            p['data'] = get_date_list(first_id,day,orders,fe1)
        
    data_new=[]
    p['list']=[]
    for da in p['data']:
        for ev_id in fe0[da]:
            p['list'].append(get_site_event(event_id = ev_id,detail=False,new=new))
        data_new.append({da:fe0[da]})
    p.update({'data':data_new})
    if request.GET.get('json',False):        
        return return_callback_http(request.GET.get("callback",None),p)
        #return HttpResponse(json.dumps(p), content_type='application/json')
    else:        
        return render_to_response(template_name,p,context_instance=RequestContext(request))

def life_app(request,template_name='showhome.html'):
    
    p={}
    p['code']=1
    p['msg']='Request is successful'
    cds = request.GET

    new = cds.get('new',None)

    cityid = cds.get('cityid',None)
    
    p['city'] = get_city_list(ty=3,new=new)
    #p['cat'] = get_cat_tag(new=new)
    p['cat'] = html_return_cat(new=new,city_id=cityid,cat_id=None,tag_id=None)
    
    #return HttpResponse(json.dumps(var), content_type='application/json')
    if request.GET.get('json',False):
        
        return return_callback_http(request.GET.get("callback",None),p)
        #return HttpResponse(json.dumps(p), content_type='application/json')
    else:
        
        return render_to_response(template_name,p,context_instance=RequestContext(request))

def about_us_page(request,template_name='aboutus.html'):
    
    return render_to_response(template_name,{},context_instance=RequestContext(request))

def find_city(request):
    rp={}
    rp['city']=getCityNameByCity(request)
    
    return return_callback_http(request.GET.get("callback",None),rp)

def test_data(request,template_name='aboutus_test.html'):
    #return render_to_response(template_name,{},context_instance=RequestContext(request))
    '''
    p={}
    
    
    p['date']=datetime.date.strftime(datetime.datetime.now(),'%Y-%m-%d')    
    p['time']=time.time()
    
    
    return HttpResponse(json.dumps(p), content_type='application/json')
    
    '''
    if request.GET.get('json',False):
        
        rp={}
        rp['city']=getCityNameByCity(request)
        rp['info']=getPageInfo('chengdu')
        return return_callback_http(request.GET.get("callback",None),rp)
        '''
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            ip =  request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        #print 'ip=',ip
        locApiUrl = 'http://apis.baidu.com/apistore/iplookupservice/iplookup?ip=%s'%ip
        
        req=urllib2.Request(locApiUrl)
        req.add_header('Content-Type', 'text/html; charset=utf-8')       
        
        
        req.add_header('apikey', '7041fb9f4922e5b76465d132da83bab6')
        
        rp = urllib2.urlopen(req,timeout=5).read()
        '''
        return HttpResponse(json.dumps(rp), content_type='application/json; charset=utf-8')
    else:
        return render_to_response(template_name,{},context_instance=RequestContext(request))

