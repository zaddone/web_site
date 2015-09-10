class Router(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'web_site':
            return 'web_site'
        else :
            return 'default'

 

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'web_site':
            return 'web_site'
        else :
            return 'default'
    
