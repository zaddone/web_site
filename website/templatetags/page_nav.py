#coding:utf-8
from django import template
from website.functions import getPageInfo
import datetime
register = template.Library()

import logging
log = logging.getLogger('XieYin.app')  
class NavMain(template.Node):
    
    def __init__(self, nodelist):
        self.nodelist = nodelist
        #log.debug('nodelist:%s',self.nodelist)

    def render(self, context):
        #log.debug('return nav')
        output = self.nodelist.render(context).replace('\n','').replace('\r','')
        
        context['Show_seo'] = getPageInfo(output)
        if not context['Show_seo']:
            outs=output.split('_')
            outstr=outs[0]
            if len(outs)>1:                
                outstr=outstr+'/'

            context['Show_seo'] = getPageInfo(outstr)
        '''
        if not context['Show_seo']:
            context['Show_seo']={}
            context['Show_seo']['title'] = u'小日子官网_小日子APP下载_小日子-感触美好生活'
            context['Show_seo']['keywords'] = u'小日子,小日子APP,小日子下载'
            context['Show_seo']['description'] = u'小日子，城市精致生活体验站，逛遍全球1000个情怀小店，感触美好生活。“小日子”APP是专注于生活方式的O2O服务平台，立足于文艺情怀，以探店发现为基础思路，以全球多城市布局为核心竞争点，解决社会新兴主流消费群体和移动互联网年轻一代的天生需求购买，帮助商户缓解推广和营销压力。'
        '''
        context['time']=datetime.datetime.strftime(datetime.datetime.today(),'%Y%m%d%H%M')
        
        return ''
 

    '''
    def render(self, context):
        context['Show_Nav']=[]   
        
        cat_n=NewCatUrl(1,self.city_py)  
        for cat in cat_n:
            nav={}
            nav['url']=cat['caturl']
            nav['name']=cat['catname']            
                
            context['Show_Nav'].append(nav)
 
        return ''
    '''

@register.tag(name="cityNav")
def do_cityNav(parser, token):    
    nodelist = parser.parse(('endcityNav',))
    parser.delete_first_token()
    return NavMain(nodelist)