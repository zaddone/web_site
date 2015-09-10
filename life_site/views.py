#coding:utf-8
import time
import datetime
from BeautifulSoup import BeautifulSoup
from django.http import HttpResponse,Http404
from django.utils import simplejson as json

from django.template import RequestContext
from website.common import get_cat_tag,get_tag_event,get_time_line,theme_page

from website.functions import getCityNameByCity,get_city_list,pagination,\
                request_val,get_url_str,return_callback_http,getPageInfo,get_site_event,\
                recommend
from django.shortcuts import render_to_response

def site_theme_page(request):
    return theme_page(request)


def get_request_val(request,arr=None,new=None,re_key=None):
    now_tag = []
    now_cat = []
    now_city=[]
    if arr:
        #arr = request_val(query)
        ci_title = get_city_list(4,new)
        cat_id_list=get_cat_tag(new=new,ty=1)
        if ci_title:
            try:
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
            except:
                pass
        if arr.has_key('tag'):
            for ta in arr['tag']:
                now_tag.append(str(ta))
        
        if cat_id_list:
            '''
            if cat_id_list.has_key('tag_id_dict') and arr.has_key('tag'):                
                now_tag=[]
                for ta in arr['tag']:
                    if ta in cat_id_list['tag_id_dict']:
                        now_tag.append(str(ta))
            '''
            if cat_id_list.has_key('cat_id_dict') and arr.has_key('cat'):
                now_cat = []
                for cat in arr['cat']:
                    if cat in cat_id_list['cat_id_dict']:
                        now_cat.append(str(cat))
        if arr.has_key('page'):
            page = arr['page'][0]
        else:
            page =1
            
        if arr.has_key('perpage'):
            perpage = arr['perpage'][0]
        else:
            perpage =15
    else:     
        page = int(request.GET.get('page',1))
        perpage =   int(request.GET.get('perpage',15))
        
    city_id=request.GET.get('cityid',None)
    cat_id=request.GET.get('catid',None)
    tag_id=request.GET.get('tagid',None)

    if city_id:
        if now_city:
            city_id = '%s,%s' % (city_id,)
    elif now_city:
        city_id=','.join(now_city)
        
    if tag_id:
        if now_tag:
            tag_id = '%s,%s' % (city_id,','.join(now_tag) )
    elif now_tag:
        tag_id = ','.join(now_tag)


    if cat_id:
        if now_cat:
            cat_id = '%s,%s' % (city_id,','.join(now_cat) )
    elif now_cat:
        cat_id =  ','.join(now_cat)
    
    if not city_id and (cat_id or tag_id or page):
        city_id='0'
    return (city_id,cat_id,tag_id,page,perpage)


def html_return_city(new,cat_id,tag_id):
    city_list=get_city_list(ty=3,new=new)
    city_list_new={}
    for city_key in city_list:
        city_list_new[city_key]=[]
        for city in city_list[city_key]:
            item={}
            if cat_id:
                item['cat']=cat_id.split(',')
            if tag_id:
                item['tag']=tag_id.split(',')
            item['city']=[city['title']]
            city['url']=get_url_str(item)
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
        
        for tag in ca['tags']:
            tag['url']=get_url_str({'city':city_py,'tag':[str(tag['id'])]})
        new_cat.append(ca)
    return new_cat
def get_current_city(city_id,new=False,city_key={}):
    data={}
    data['Current_city']=[]
    if  city_id :      
        citys=city_id.split(',')
        city_ids=get_city_list(ty=1,new=new)       
        
        for ci in citys:
            if int(ci)==0:
                data['Current_city'].append(city_key['list'])
                break
            if int(ci) in city_ids:            
                data['Current_city'].append(city_ids[int(ci)])
    return data

def get_current_cat_and_tag(cat_id,tag_id,new=False):
    data={}
    data['Current_cat']=[]
    data['Current_tag']=[]
    if tag_id or cat_id:
        #br=False
        cat_id_list=get_cat_tag(new=new,ty=1)        
        if cat_id:
            
            for ca in cat_id.split(','):
                data['Current_cat'].append(cat_id_list['cat_id_dict'][int(ca)])
                
            if not data['Current_cat']:
                    return False

        if tag_id:
            for ta in tag_id.split(','):
                try:
                    data['Current_tag'].append(cat_id_list['tag_id_dict'][int(ta)])
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
    re_key={'domestic':{"name":u"国内","title": "domestic"},
            'abroad':{"name":u"国外","title": "abroad"},
            'list':{"name":u"全国","title": "list"},
           }
    data['Current_city']=[]
    data['Current_cat']=[]
    data['Current_tag']=[]
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
    
    data['city_list']=html_return_city(new=new,cat_id=cat_id,tag_id=cat_id)
    if 'city' in query_arr:
        for ci in query_arr['city']:
            
            if ci in re_key:
                data['Current_city'].append(re_key[ci])
    if  not data['Current_city']:     
        data.update(get_current_city(city_id = city_id,new=new,city_key=re_key))

    if not data['Current_city']:
        return data
        
    data['cat'] = html_return_cat(new=new,city_id=data['Current_city'],cat_id=cat_id,tag_id=cat_id)
    #city_id=None

    data['Current_page_count'] = 0
    event_id_list_count =data['count'] = get_tag_event(tagid=tag_id,catid=cat_id,cityid=city_id,new=new,perpage=None)
    if not event_id_list_count or  event_id_list_count < data['Current_page']:
        return data
    data['Current_page_count'] = event_id_list_count/data['Current_perpage']+1 if event_id_list_count%data['Current_perpage'] else 0
    
    data['pagination']=pagination(request,event_id_list_count,data['Current_perpage'],pageNum=10,nowCity=city_id,query=query )
    
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

    new=request.GET.get('new',1)
    data = get_site_event(event_id = int(query),detail=True,new=new)

        
    
    data['ad']=request.GET.get('ad',False)
    data['hot_tag']=get_hot_tag()
    def get_tag_str(_tag=data['tag']):
        tags=''
        for tag in _tag:
            if type(tag)==tuple:
                tags ='%s%s' %( tags,tag[1])
            else:
                tags ='%s%s' %( tags,tag)
        return tags
    data['tags'] = get_tag_str()
    data['more']= recommend(data['id'], data['city_name'], tags =data['tags'], new=new )
    #return HttpResponse(json.dumps(var), content_type='application/json')
    if request.GET.get('json',False):
        return return_callback_http(request.GET.get("callback",None),data)
        #return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        if request.GET.get('share',False):
            template_name='showpage_share.html'
        return render_to_response(template_name,data,context_instance=RequestContext(request))


def find_first_data(date,order=None,fe_dict={},fe_list=[],number=0):
    if number>9:
        return None
    date_str = datetime.datetime.strftime(date, '%Y-%m-%d')
    if date_str in fe_dict:
        #return fe_dict[date_str]
        return fe_list.index(date_str)
        #return fe0[date_str]
    else:
        #return 'not find'
        oneday = datetime.timedelta(days=1)
        if order:
            date=date-oneday
        else:
            date=date+oneday
        number+=1
        return find_first_data(date,order,fe_dict,fe_list,number)
    
def life_home(request,template_name='showhome.html'):
    
    p={}
    p['code']=1
    p['msg']='Request is successful'
    cds = request.GET
    date = cds.get('date',None)
    day = int(cds.get('day',10))
    new = cds.get('new',None)
    orders = 0 if cds.get('order',1)=='0' else cds.get('order',1)
    cityid = cds.get('cityid',None)
    
    p['city'] = get_city_list(ty=3,new=new)
    #p['cat'] = get_cat_tag(new=new)
    p['cat'] = html_return_cat(new=new,city_id=cityid,cat_id=None,tag_id=None)
    if not date:
        date=datetime.date.today()
    else:
        try:
            date=datetime.datetime.strptime( date, "%Y-%m-%d").date()
        except:
            try:
                date = time.strptime(date,"%Y-%m-%d %H:%M:%S")
                date=datetime.datetime(* date[:6])
            except:
                date=datetime.date.today()


    fe0 = get_time_line(0, city_id = cityid, new = new)

        
    fe1 = get_time_line(1, city_id = cityid, new = new)
    first_id = find_first_data(date,orders,fe0,fe1)
    
    p['first_id']=fe1
    
    if orders:
        if not first_id:
            first_id = 0
            
        end=first_id+day-1

        p['data']=fe1[first_id:end]
    else:
        if not first_id:
            first_id = 1
            
        begin = first_id-day+1
        if begin<0:
            begin = 0
        p['data']=fe1[begin :first_id]
    
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

