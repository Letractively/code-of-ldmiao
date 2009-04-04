#coding:utf-8
import wsgiref.handlers
import os
from functools import wraps
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import users
import methods,logging
from django.utils import simplejson

from google.appengine.ext import db

adminFlag=True

admin_emails = set(['ldmiao@gmail.com'])

class AdminControl(webapp.RequestHandler):
    def render(self,template_file,template_value):
        path=os.path.join(os.path.dirname(__file__),template_file)
        self.response.out.write(template.render(path, template_value))
    def returnjson(self,dit):
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(simplejson.dumps(dit))
        
def requires_admin(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        global admin_emails
        user = users.get_current_user()
        #if not users.is_current_user_admin() and adminFlag:
        if user and user.email():
            if user.email() in admin_emails:
                return method(self, *args, **kwargs)
            
        self.redirect(users.create_login_url(self.request.uri))
        
    return wrapper

class Admin_Upload(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/upload.html', {})
    @requires_admin
    def post(self):
        bf=self.request.get("file")
        if not bf:
            return self.redirect('/admin/upload/')
#        name=self.request.body_file.vars['file'].filename
        mime = self.request.body_file.vars['file'].headers['content-type']
        if mime.find('image')==-1:
             return self.redirect('/admin/upload/')
        description=self.request.get("description")
        image=methods.addImage( mime, description, bf)
        
        self.redirect('/show/%s/' %image.id)

class Admin_Upload2(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/upload2.html', {})
    #@requires_admin
    def post(self):
        dit={"result":"error"}
        bf=self.request.get("Filedata")
        if not bf:
            return self.returnjson(dit)
        image=methods.addImage2(bf)
        if not image:
             return self.returnjson(dit)
        dit["result"]="ok"
        dit["id"]=image.id
        return self.returnjson(dit)

class Admin_Upload3(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/upload3.html', {})
    #@requires_admin
    def post(self):
        dit={"result":"error"}
        bf=self.request.get("Filedata")
        if not bf:
            return self.returnjson(dit)
        image=methods.addImage2(bf)
        if not image:
             return self.returnjson(dit)
        dit["result"]="ok"
        dit["id"]=image.id
        return self.returnjson(dit)
        
class Admin_UploadByURL(AdminControl):
    @requires_admin
    def get(self):
        self.render('views/upload3.html', {})
    #@requires_admin
    def post(self):
        dit={"result":"error"}
        bf=self.request.get("Filedata")
        if not bf:
            return self.returnjson(dit)
        image=methods.addImage2(bf)
        if not image:
             return self.returnjson(dit)
        dit["result"]="ok"
        dit["id"]=image.id
        return self.returnjson(dit)

class Delete_Image(AdminControl):
    @requires_admin
    def get(self,key):
        methods.delImage(key)
        self.redirect('/')
        
class Delete_Image_ID(AdminControl):
    @requires_admin
    def get(self,id):
        methods.delImageByid(id)
        self.redirect('/')

class Admin_Login(AdminControl):
    @requires_admin
    def get(self):
        self.redirect('/')

class Admin_Page(AdminControl):
        
    @requires_admin
    def get(self):
        action = self.request.get('action')
        
        output = "0"
        if action=='clear':
            images=methods.getImages(count=50)
            if(len(images)>0):
                output = str(len(images))
            db.delete(images)
            self.response.out.write(output)
        elif action=='getrss':
            rss_template = methods.get_rss_template()
            rss = memcache.get("rss_content")
            if rss:
                #self.response.headers['Content-Type'] = "application/rss+xml"
                self.response.headers['Content-Type'] = "text/xml"
                self.response.out.write(rss_template%(rss))
            else:
                self.response.out.write('not right!')
        elif action=='regeneraterss':
            generate = memcache.get("rss_generate")
            rss = memcache.get("rss_content")
            lastImage_date = memcache.get("rss_lastImage_date")
            
            if generate=='create':
                memcache.delete('rss_content')
                memcache.delete('rss_lastImage_date')
                memcache.set("rss_generate", 'not_create')
                logging.info('set rss_generate to not_create')
                lastImage_date = None
                rss = ''
                
            if rss and lastImage_date:
                pass
            else:
                lastImage_date = None
                rss = ''
            
            images=methods.getImagesBefore(count=50, lastImage_date=lastImage_date)
            if(len(images)>0):
                rss += methods.generateRSSItems(images)
                length = len(images)
                lastImage_date = images[length-1].created_at
                output = str(length)
                memcache.set('rss_content', rss)
                memcache.set('rss_lastImage_date', lastImage_date)
                
            else:
                methods.persistRSS()
                memcache.set("rss_generate", 'create')
                logging.info('set rss_generate to create')
            
            self.response.out.write(output)
        else:
            self.render('views/admin.html', {})

def main():
    application = webapp.WSGIApplication(
                                       [(r'/admin/upload/', Admin_Upload),
                                        (r'/admin/upload2/', Admin_Upload2),
                                        (r'/admin/upload3/', Admin_Upload3),
                                        (r'/admin/saveurl/', Admin_UploadByURL),
                                        (r'/admin/del/(?P<key>[a-z,A-Z,0-9]+)', Delete_Image),
                                        (r'/admin/delid/(?P<id>[0-9]+)/', Delete_Image_ID),
                                        (r'/admin/', Admin_Page),
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()