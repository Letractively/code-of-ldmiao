#Copyright Jon Berg , turtlemeat.com

import string,cgi,time,os
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import pri

photo_dir_path = "C:\\Photo"

class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        global photo_dir_path
        try:
            real_path = photo_dir_path + '/' + self.path
            print real_path
            if os.path.isdir(real_path):
                body = '\n<ul>\n'
                for name in os.listdir(real_path):
                    new_path = self.path+'/'+name
                    while new_path.startswith('//'):
                        new_path = new_path[1:]
                    body += '''<li><a href="/%s">%s</a></li>\n'''%(new_path, name)
                body += '</ul>\n'
                html = '''<html><head></head><body style="width:320px; height:480px;">%s</body></html>'''%(body)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html)
                return
            else:
                f = open(photo_dir_path + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return   
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

