#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import urllib
import gd
import Image
from itertools import *
from math import *
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from StringIO import StringIO

sources = {
    'kh33': {'url': 'http://kh.google.com/kh?v=33', 'filetype': 'jpg'},
    'w2.86': {'url': 'http://mt.google.com/mt?v=w2.86', 'filetype': 'png'},
    'w2t.86': {'url': 'http://mt.google.com/mt?v=w2t.86', 'filetype': 'png'},
    'cn1.5': {'url': 'http://mt.google.cn/mt?v=cn1.5', 'filetype': 'png'},
}

class RequestHandler(BaseHTTPRequestHandler):

    server_version = 'GoogleMaps'

    error_content_type = 'text/html; charset=utf-8'
    error_message_format = '<?xml version="1.0" encoding="utf-8"?>' \
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">' \
        '<html xmlns="http://www.w3.org/1999/xhtml">' \
        '<head><meta http-equiv="Content-Type" content="' + error_content_type + '"><title>%(code)s %(message)s</title></head>' \
        '<body><h1>%(message)s</h1><p>%(explain)s</p></body>' \
        '</html>'

    def do_GET(self):
        try:
            path, query = (self.path.split('?', 1) + [None])[:2]
            source = path[1:]
            if source not in sources:
                self.send_error(404)
                return
            if query is not None:
                params = dict(imap(lambda x: (list(imap(urllib.unquote, x.split('=', 1))) + [None])[:2], query.split('&')))
            bbox, width, height = imap(float, params['bbox'].split(',')), int(params['width']), int(params['height'])
            lon1, lat1, lon2, lat2 = imap(radians, bbox)
            x1, y1 = lon1 / 2.0 / pi + 0.5, log((1.0 + sin(lat1)) / (1.0 - sin(lat1))) / 4.0 / pi + 0.5
            x2, y2 = lon2 / 2.0 / pi + 0.5, log((1.0 + sin(lat2)) / (1.0 - sin(lat2))) / 4.0 / pi + 0.5
            z = min(max(int(ceil(log(min(width / ((x2 - x1) * 256), height / ((y2 - y1) * 256)), 2))), 0), 17)
            iw, ih = int(round(ldexp((x2 - x1) * 256, z))), int(round(ldexp((y2 - y1) * 256, z)))
            ix_list = range(int(floor((floor(ldexp(x1, z)) - ldexp(x1, z)) / ldexp(x2 - x1, z) * iw)), iw, 256)
            iy_list = range(int(floor((floor(ldexp(y1, z)) - ldexp(y1, z)) / ldexp(y2 - y1, z) * ih)), ih, 256)
            image = gd.image((iw, ih)) if sources[source]['filetype'] == 'png' else Image.new('RGB', (iw, ih))
            for ix, iy in product(ix_list, iy_list):
                x = int(floor(ldexp(x1, z))) + (ix - ix_list[0]) // 256
                y = int(floor(ldexp(y1, z))) + (iy - iy_list[0]) // 256
                url = '%s&x=%d&y=%d&z=%d' % (sources[source]['url'], x, 2 ** z - y - 1, z)
                dirname = os.path.join(os.path.dirname(__file__), source)
                filename = '%02d-%06d-%06d.%s' % (z, 2 ** z - y - 1, x, sources[source]['filetype'])
                try:
                    with file(os.path.join(dirname, filename), 'r') as f:
                        if sources[source]['filetype'] == 'png':
                            gd.image(f, sources[source]['filetype']).copyTo(image, (ix, ih - iy - 256))
                        else:
                            image.paste(Image.open(f), (ix, ih - iy - 256))
                except IOError:
                    print >> sys.stderr, 'GET %s...' % url,
                    try:
                        data = urllib.urlopen(url).read()
                    except Exception as exc:
                        print >> sys.stderr, 'ERROR: %s' % exc
                        continue
                    print >> sys.stderr, 'OK'
                    try:
                        if sources[source]['filetype'] == 'png':
                            gd.image(StringIO(data), sources[source]['filetype']).copyTo(image, (ix, ih - iy - 256))
                        else:
                            image.paste(Image.open(StringIO(data)), (ix, ih - iy - 256))
                    except Exception as exc:
                        print >> sys.stderr, exc
                        continue
                    try:
                        os.makedirs(dirname)
                    except OSError:
                        pass
                    try:
                        with file(os.path.join(dirname, filename), 'w') as f:
                            f.write(data)
                    except IOError:
                        pass
        except Exception as exc:
            print >> sys.stderr, exc
            self.send_error(500)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.end_headers()
        if sources[source]['filetype'] == 'png':
            image.writePng(self.wfile)
        else:
            image.save(self.wfile, 'PNG')

HTTPServer(('', 8000), RequestHandler).serve_forever()