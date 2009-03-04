import string,cgi,time,os
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
#import pri

import process

photo_dir_path = "C:\\Photo"
photo_dir_path = "D:/Documents/ScrapBook/data"

class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        reload(process)
        process.processGET(self)
        

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
        print 'HTTP Server started at port:%d'%(port)
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

