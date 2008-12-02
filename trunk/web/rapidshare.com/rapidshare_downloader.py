#!/usr/bin/env python

import sys, urllib2, re, time, os

usage_string = 'Usage: python -u rapidget.py check|download < url_file'

if len(sys.argv)!=2:
    print usage_string
    sys.exit()
elif sys.argv[1]=='check':
    download = False
elif sys.argv[1]=='download':
    download = True
else:
    print usage_string
    sys.exit()

page2_url_pattern = r'<form id="ff" action="(.*)" method="post">'
file_url_pattern = r'<input  type="radio" name="mirror" onclick="document.dlf.action=\\\'(.*)\\\';" /> (.*)<br />'

for src_url in sys.stdin:
    src_url = src_url.strip()
    if not src_url.startswith('http://'):
        src_url = 'http://'+src_url

    print '%s...'%src_url,
    page1 = urllib2.urlopen(src_url).read()
    t = re.search(page2_url_pattern, page1)
    if t is None:
        print 'ERROR'
        open(src_url.split('/')[-1]+'.err.html', 'w').write(page1)
        continue
    page2_url = t.group(1)
    print 'valid'

    if download:
        while True:
            page2 = urllib2.urlopen(page2_url, data='dl.start=Free&submit=Free%20user').read()
            file_urls = re.findall(file_url_pattern, page2)
            if len(file_urls)>0:
                break
            print '\tNo download link, wait 60 seconds before retry...'
            time.sleep(60)
        file_url = file_urls[0][0]
        print file_url
        print '\tGet link, wait 120 seconds before download is ready...'
        time.sleep(120)
        os.system('wget %s'%file_url)