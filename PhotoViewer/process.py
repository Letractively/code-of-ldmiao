import string,cgi,time,os
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import pri
import urllib

import PIL
from PIL import Image

photo_dir_path = "C:\\Photo"
#photo_dir_path = "D:/Documents/ScrapBook/data"

def filesize(path):
    return os.stat(path)[6]

def getNextFromPath(current_path):
    global photo_dir_path
    lastsep = current_path.rfind('/')
    current_dir = current_path[:lastsep]
    absolute_current_dir = photo_dir_path+current_path[:lastsep]
    current_name = current_path[lastsep+1:]
    if os.path.isdir(absolute_current_dir):
        print absolute_current_dir
        namelist = os.listdir(absolute_current_dir)
        #namelist = namelist.sort()
        isOK = 0
        for name in namelist:
            if isOK==1:
                return current_dir+'/'+name
            if name==current_name:
                isOK = 1

def processGET(handler):
    global photo_dir_path
    try:
        print 'request path:', handler.path
        
        if handler.path.startswith('/?img='):
            body = '''<img src="%s"/>'''%(unicode(urllib.unquote(handler.path[len('/?img='):]), 'utf-8','ignore').encode('cp936'))
            html = '''<html><head></head><body style="width:320px; height:480px; font-size: 50px">%s</body></html>'''%(body)
            handler.send_response(200)
            handler.send_header('Content-type', 'text/html')
            handler.end_headers()
            handler.wfile.write(html)
            return
        elif handler.path.startswith('/?next='):
            current_img_path = unicode(urllib.unquote(handler.path[len('/?next='):]), 'utf-8','ignore').encode('cp936')
            next_img_path = getNextFromPath(current_img_path)
            body = '''<img src="%s"/>'''%(next_img_path)
            html = '''<html><head></head><body style="width:320px; height:480px; font-size: 50px">%s</body></html>'''%(body)
            handler.send_response(200)
            handler.send_header('Content-type', 'text/html')
            handler.end_headers()
            handler.wfile.write(html)
            return
        
        real_path = photo_dir_path + handler.path
        real_path = unicode(urllib.unquote(real_path), 'utf-8','ignore').encode('cp936')
        
        if os.path.exists(real_path):
            #print real_path
            if os.path.isdir(real_path):
                body = '\n<ul>\n'
                for name in os.listdir(real_path):
                    new_path = handler.path+'/'+name
                    while new_path.startswith('//'):
                        new_path = new_path[1:]
                    if os.path.isdir(real_path+'/'+name):
                        body += '''<li><a href="%s">%s</a></li>\n'''%(new_path, name)
                    else:
                        body += '''<li><a href="/?img=%s">%s</a> <a href='/?next=%s'>next</a></li>\n'''%(new_path, name, new_path)
                body += '</ul>\n'
                html = '''<html><head></head><body style="width:320px; height:480px; font-size: 18pt;">%s</body></html>'''%(body)
                handler.send_response(200)
                handler.send_header('Content-type', 'text/html')
                handler.end_headers()
                handler.wfile.write(html)
            else:
                tmp_img = Image.open(real_path)
                if tmp_img.size[0] > tmp_img.size[1]:
                    tmp_img = tmp_img.rotate(270)
                
                width = 640
                wpercent = (width/float(tmp_img.size[0]))
                hsize = int((float(tmp_img.size[1])*float(wpercent)))
                tmp_img = tmp_img.resize((width, hsize), PIL.Image.ANTIALIAS)
                
                #if tmp_img.size[1] > 480:
                #    crop_margin = (tmp_img.size[1]-480)/2
                tmp_img = tmp_img.crop((30, 30, tmp_img.size[0]-60, tmp_img.size[1]-60))
                
                tmp_img.save('temp_img.jpg')
                
                #f = open(real_path, 'rb')
                f = open('temp_img.jpg', 'rb')
                
                content_type = 'image/jpeg'
                lowered_path = handler.path.lower()
                if lowered_path.endswith('png'):
                    content_type = 'image/png'
                if lowered_path.endswith('gif'):
                    content_type = 'image/gif'
                
                handler.send_response(200)
                handler.send_header('Content-type', content_type)
                #print filesize(real_path)
                handler.send_header('Content-Length', filesize(real_path))
                handler.end_headers()
                handler.wfile.write(f.read())
                f.close()
            
    except IOError:
        handler.send_error(404,'File Not Found: %s' % handler.path)