#coding:utf-8
import wsgiref.handlers
import os
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import users
import methods
import logging

page = 0

def format_date(dt):
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

class PublicPage(webapp.RequestHandler):
    def render(self, template_file, template_value):
        path = os.path.join(os.path.dirname(__file__), template_file)
        self.response.out.write(template.render(path, template_value))
    
    def error(self,code):
        if code==400:
            self.response.set_status(code)
        else:
            self.response.set_status(code)
            
    def is_admin(self):
        return users.is_current_user_admin()
    
    def head(self, *args):
        return self.get(*args) 
    
class MainPage(PublicPage):
    def get(self,page):
        index=0 if page=="" else int(page)
        images=methods.getAllImages(index)
        prev,next=methods.getPageing(len(images), index)
        template_value={"images":images[:48],"prev":prev,"next":next}
        self.render('views/index.html', template_value)

class SlidePage(PublicPage):
    def get(self):
        images=methods.getImages()
        template_value={"images":images}
        self.render('views/slide.html', template_value)

class FlashPage(PublicPage):
    def get(self):
        page = self.request.get('page')
        p = "0" if page=="" or page==None else page
        memcache.set("flash_page_key", p, 60)
        
        logging.info(page)
        
        self.render('views/flash.html', {})
        #self.render('views/flash2.html', {})

class CoverFlowPage(PublicPage):
    def get(self):
        self.render('views/coverflow.html', {})
        
        #images=methods.getImages()
        #template_value={"images":images}
        #self.render('views/jscoverflow.html', template_value)

class XMLPage(PublicPage):
    def get(self):
        images=methods.getImages()
        template_value={"images":images}
        self.response.headers['Content-Type'] = "text/xml"
        self.render('views/xml.html', template_value)

class FlashXML(PublicPage):
    def get(self):
        #page = self.request.get('page')
        #index=0 if page=="" or page==None else 100*int(page)
        
        page = memcache.get("flash_page_key")
        if page:
            page = int(page)
        else:
            page = 0
        
        logging.info(page)
        index = 300*int(page)
        
        images=methods.getImages(count=300, offset=index)
        template_value={"images":images}
        self.response.headers['Content-Type'] = "text/xml"
        self.render('views/gallery.xml', template_value)
        
        #self.response.headers['Content-Type'] = "text/plain"
        #self.render('views/gallery2.xml', template_value)
        
class RSSPage(PublicPage):
    def get(self):
        images=methods.getImages(count=300)
        template_value={"images": images}
        
        self.response.headers['Content-Type'] = "application/rss+xml"
        self.render('views/rss.xml', template_value)

class ShowImage(PublicPage):
    def get(self,id):
        image=methods.getImage(id)
        if not image:return self.error(404)
        template_value={"image":image,"admin":self.is_admin()}
        self.render('views/show.html', template_value)
    
class GetImage(PublicPage):
    def get(self,size,id):
        logging.info("size: %s"%(size))
        dic=self.request.headers
        key=dic.get("If-None-Match")
        self.response.headers['ETag']=size+id
        if key and key==size+id:
            return self.error(304)
        image=methods.downImage(id, size)
        if not image:
            return self.error(404)
        self.response.headers['Content-Type'] = str(image.mime)
        self.response.headers['Cache-Control']="max-age=315360000"
        self.response.headers['Last-Modified']=format_date(image.created_at)
        self.response.out.write(image.bf)

class Error(PublicPage):
    def get(self):
        return self.error(404)

def main():
    application = webapp.WSGIApplication(
                                       [(r'/slide/?', SlidePage),
                                        (r'/coverflow/?', CoverFlowPage),
                                        (r'/flash/?', FlashPage),
                                        (r'/flash/gallery\..*', FlashXML),
                                        (r'/xml/?', XMLPage),
                                        (r'/(?P<size>image)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/(?P<size>s)/(?P<id>[0-9]+)/?',GetImage),
                                        (r'/show/(?P<id>[0-9]+)/',ShowImage),
                                        (r'/(?P<page>[0-9]*)/?', MainPage),
                                        (r'/photos.rss', RSSPage),
                                        ('.*',Error)
                                       ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()