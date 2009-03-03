#Copyright Jon Berg , turtlemeat.com

import string,cgi,time,os
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import pri
import urllib

import PIL
from PIL import Image

photo_dir_path = "C:\\Photo"
photo_dir_path = "D:/Documents/ScrapBook/data"

def filesize(path):
    return os.stat(path)[6]

class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        global photo_dir_path
        try:
            real_path = photo_dir_path + self.path
            real_path = unicode(urllib.unquote(real_path), 'utf-8','ignore').encode('cp936')
            print real_path
            if os.path.exists(real_path):
                if os.path.isdir(real_path):
                    body = '\n<ul>\n'
                    for name in os.listdir(real_path):
                        new_path = self.path+'/'+name
                        while new_path.startswith('/'):
                            new_path = new_path[1:]
                        body += '''<li><a href="/%s">%s</a></li>\n'''%(new_path, name)
                    body += '</ul>\n'
                    html = '''<html><head></head><body style="width:320px; height:480px; font-size: 50px">%s</body></html>'''%(body)
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html)
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
                    tmp_img = tmp_img.crop((40, 40, tmp_img.size[0]-80, tmp_img.size[1]-80))
                    
                    tmp_img.save('temp_img.jpg')
                    
                    #f = open(real_path, 'rb')
                    f = open('temp_img.jpg', 'rb')
                    
                    content_type = 'image/jpeg'
                    lowered_path = self.path.lower()
                    if lowered_path.endswith('png'):
                        content_type = 'image/png'
                    if lowered_path.endswith('gif'):
                        content_type = 'image/gif'
                    
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    print filesize(real_path)
                    self.send_header('Content-Length', filesize(real_path))
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()
                
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
     

    def do_POST(self):
        global rootnode
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            self.send_response(301)
            
            self.end_headers()
            upfilecontent = query.get('upfile')
            print "filecontent", upfilecontent[0]
            self.wfile.write("<HTML>POST OK.<BR><BR>");
            self.wfile.write(upfilecontent[0]);
            
        except :
            pass

def main():
    try:
        port = 80
        server = HTTPServer(('', port), MyHandler)
        print 'started httpserver at port:%d'%(port)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

