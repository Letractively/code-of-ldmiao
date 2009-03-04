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
            lowered_name = name.lower()
            if isOK==1 and os.path.isfile(absolute_current_dir+'/'+name) and (lowered_name.endswith('jpg') or lowered_name.endswith('jpeg') or lowered_name.endswith('png') or lowered_name.endswith('gif')):
                return current_dir+'/'+name
            if name==current_name:
                isOK = 1

def getImageViewPage(handler, img_path):
    head_script = '''
        var img_path = '%s';
        function loadNextImg(){
            setTimeout('gotoNextImage()',3000);
        }
        function gotoNextImage(){
            window.location.href='/?next='+img_path;
            //document.getElementById('image').src = '/?nextimage='+img_path;
            //setTimeout('gotoNextImage()', 3000);
        }
    '''%(img_path)
    body = '''<img id="image" style="" src="%s"/>'''%(img_path)
    html = '''<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /><title>%s</title>\n<script>%s</script>\n</head>\n<body onload="loadNextImg()" style="width:320px; height:480px; font-size: 60px">%s</body></html>'''%(img_path, head_script, body)
    handler.send_response(200)
    handler.send_header('Content-type', 'text/html')
    handler.end_headers()
    handler.wfile.write(html.encode('utf-8'))
    
def processGET(handler):
    global photo_dir_path
    try:
        print 'request path:', handler.path
        
        req_path = handler.path
        
        if req_path.startswith('/favicon.ico'):
            return
        elif req_path.startswith('/?img='):
            getImageViewPage(handler, unicode(urllib.unquote(req_path[len('/?img='):]), 'utf-8','ignore'))
            return
        elif req_path.startswith('/?next='):
            current_img_path = unicode(urllib.unquote(req_path[len('/?next='):]), 'utf-8','ignore')
            next_img_path = getNextFromPath(current_img_path)
            if next_img_path:
                getImageViewPage(handler, next_img_path)
                return
            else:
                lastsep = req_path.rfind('/')
                req_path = req_path[len('/?next='):lastsep]
        
        real_path = photo_dir_path + req_path
        real_path = unicode(urllib.unquote(real_path), 'utf-8','ignore')
        #print 'real path 1:'+real_path
        if os.path.exists(real_path):
            #print 'real path 2:'+real_path
            if os.path.isdir(real_path):
                lastsep = req_path.rfind('/')
                parent_path = req_path[:lastsep]
                if lastsep == 0:
                    parent_path = '/'
                body = u'\n<ul style="width:900px;">\n<li><a href="%s">Parent Folders</a></li>'%(parent_path)
                for name in os.listdir(real_path):
                    new_path = req_path+'/'+name
                    while new_path.startswith('//'):
                        new_path = new_path[1:]
                    if os.path.isdir(real_path+'/'+name):
                        body += u'''<li><a href="%s">%s</a></li>\n'''%(new_path, name)
                    else:
                        lowered_name = name.lower()
                        if lowered_name.endswith('jpg') or lowered_name.endswith('jpeg') or lowered_name.endswith('png') or lowered_name.endswith('gif'):
                            body += u'''<li><a href="/?img=%s">%s</a> <a href='/?next=%s'>next</a></li>\n'''%(new_path, name, new_path)
                body += u'<li><a href="%s">Parent Folders</a></li>\n</ul>\n'%(req_path[:req_path.rfind('/')])
                html = u'''<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head><body style="width:320px; height:480px; font-size: 40pt;">%s</body></html>'''%(body)
                handler.send_response(200)
                handler.send_header('Content-type', 'text/html')
                handler.end_headers()
                handler.wfile.write(html.encode('utf-8'))
            else:
                tmp_img = Image.open(real_path)
                if tmp_img.size[0] > tmp_img.size[1]:
                    tmp_img = tmp_img.rotate(270)
                
                width = 900
                wpercent = (width/float(tmp_img.size[0]))
                hsize = int((float(tmp_img.size[1])*float(wpercent)))
                tmp_img = tmp_img.resize((width, hsize), PIL.Image.ANTIALIAS)
                
                #if tmp_img.size[1] > 480:
                #    crop_margin = (tmp_img.size[1]-480)/2
                #tmp_img = tmp_img.crop((30, 0, tmp_img.size[0]-30, tmp_img.size[1]))
                
                tmp_img.save('temp_img.jpg')
                
                #f = open(real_path, 'rb')
                f = open('temp_img.jpg', 'rb')
                
                content_type = 'image/jpeg'
                lowered_path = req_path.lower()
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