# -*- coding: utf-8 -*-

import MySQLdb
import urllib2, cookielib, re, os, time, sys, urllib, codecs,random

def get(url):
    cookiefile = 'cookies.txt'
    proxy = {'http': 'http://web-proxy.hpl.hp.com:8088'}

    cj = cookielib.MozillaCookieJar()
    if os.path.isfile(cookiefile):
        #print 'loading cookies...'
        cj.load(cookiefile)
    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    data = None
    headers =  {'User-agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
                'Referer':'http://www.google.com/reader/view/',
##                'Accept-Encoding':'gzip,deflate',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': 300,
                'Proxy-Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

    
    #print 'getting a page[url=%(url)s]...' % {'url':url}
    req = urllib2.Request(url, data, headers)
    handle = urllib2.urlopen(req)
    #print handle.info()
   
    html = handle.read()    
    handle.close()
    return html

def writedb(conn, title, url, tags, datelong):
    cursor = conn.cursor()
    date = datetime.datetime.strptime(time.ctime(datelong), '%a %b %d %H:%M:%S %Y')
    sql = 'INSERT reader(title, url, tags, date) VALUES(%s,%s,%s,%s)'
    cursor.execute(sql, (title, url, tags, date))
    cursor.close()

def unicode_repl(o):     
    return unichr(int(o.group(1), 16))

def g_decode(content):
    pattern = re.compile('\\\u([0-9a-zA-Z]{4})', re.DOTALL)
    content = re.sub(pattern, unicode_repl, content)
    return content

def parse_chunk(data, conn):
    data = data.replace('true', 'True')
    data = data.replace('false', 'False')
    chunk = eval(data)
    # chunk is a dictionary
    # keys: {updated, title, continuation, self, alternate, items, id}
    
    updated = -1
    if 'updated' in chunk:
        updated = chunk['updated']

    continuation = ''        
    if 'continuation' in chunk:
        continuation = chunk['continuation']

    items = []
    if 'items' in chunk:
        items = chunk['items']
        
    print '%s bookmarks retrieved' % (str(len(items)))
    for item in items:
        # item is a dictionary
        # keys: {origin, updated, author, title, alternate, comments,
        #       summary, crawlTimeMsec,
        #       annotations, published, id, categories}
        #       - summary is a dict
        #       - categories is a tag list

        updated = item['updated']        
        #title = g_decode(item['title'])
        #tagString = ''
        #tags = item['categories']
        #tags = tags[max(0, len(tags) - 10):]
        #for tag in tags:
        #    if len(tagString) == 0:
        #        tagString += g_decode(tag)
        #    else:
        #        tagString += ', ' + g_decode(tag)
            
        summary = item['summary']
        # summary is a dictionary
        # keys: {content, direction}
        content = g_decode(summary['content'])
        #print content
        
        #print '+title: "%s"' % (title)
        #print '---tags[%d]: %s' % (len(tags), tagString)

        pattern = re.compile(r'<a href="http\://delicious\.com/post\?url=(.*?)&amp;title=(.*?)&amp;copyuser=&amp;copytags=(.*?)&amp;', re.DOTALL)
        obj = re.search(pattern, content)
        url = urllib.unquote_plus(obj.group(1)).encode('iso-8859-1')
        title = urllib.unquote_plus(obj.group(2)).encode('iso-8859-1')
        tags = urllib.unquote_plus(obj.group(3)).replace(' ', ',').encode('iso-8859-1')
        
        writedb(conn, title, url, tags, updated)
    conn.commit()
    return [updated, continuation]


if __name__ == '__main__':
    conn = MySQLdb.connect(host = "hplcws4.hpl.hp.com", user = "om", passwd = "Sh3ngWen!@3", db = "reviews", charset = 'utf8', use_unicode = True)

##    r = open('chunk\\5')
##    x= r.read()
##    r.close()
##    print parse_chunk(x, conn)
   
##    url = 'http://www.google.com/reader/api/0/stream/contents/feed/' \
##          'http%3A%2F%2Ffeeds.delicious.com%2Fv2%2Frss%2F?r=n&' \
##          'n=40&client=scroll'
    url = 'http://www.google.com/reader/api/0/stream/contents/feed/' \
          'http%3A%2F%2Ffeeds.delicious.com%2Fv2%2Frss%2F?r=n&' \
          'c=' + 'CMHLvtTsm5UC' + '&n=40&client=scroll'

    cnt = 0
    while True:
        print 'send a request [%s]' % (str(cnt))
        data = get(url)

        w = open('chunk\\' + str(cnt), 'w')
        w.write(data)
        w.close()
        para = parse_chunk(data, conn)
        
        print '\tupdated: ' + str(para[0])
        print '\tcontinuation: ' + para[1]
        
        cnt += 1
        time.sleep(random.randint(5,15))

        url = 'http://www.google.com/reader/api/0/stream/contents/feed/' \
          'http%3A%2F%2Ffeeds.delicious.com%2Fv2%2Frss%2F?r=n&' \
          'c=' + para[1] + '&n=40&client=scroll'
    conn.close()
