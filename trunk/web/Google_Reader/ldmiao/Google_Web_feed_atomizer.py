import sys
import httplib2
import urllib, urllib2
from xml2dict import XML2Dict

class feedconverter(object):
    gfeed = "http://www.google.com/reader/atom/feed/%s"
    gfeed_limited = "http://www.google.com/reader/atom/feed/%s?r=n&n=%i"
    reader_prep_uri = "http://www.google.com/reader/api/0/token"
    def __init__(self, user, passwd):
        '''
        user - Google e-mail including the "@gmail.com"
        passwd - password
        '''
        #FIXME: might as well use httplib2 here as well
        # get an AuthToken from Google accounts
        # http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html#Parameters
        auth_uri = 'https://www.google.com/accounts/ClientLogin'
        authreq_data = urllib.urlencode({ "Email": user,
                                          "Passwd":  passwd,
                                          "service": "reader",
                                          "source":  "Amara demo",
                                          "accountType": "GOOGLE",
                                          #"continue": "http://www.google.com/",
                                          })
        auth_req = urllib2.Request(auth_uri, data=authreq_data)
        auth_resp = urllib2.urlopen(auth_req)
        auth_resp_body = auth_resp.read()
        auth_resp_dict = dict(x.split("=")
                              for x in auth_resp_body.split("\n") if x)
        self.auth = auth_resp_dict["Auth"].strip()
        self.sid = auth_resp_dict["SID"].strip()
        self.h = httplib2.Http()
        self.h.follow_all_redirects = True
        self._update_token()
        return

    def _update_token(self):
        headers = {'Cookie': 'SID='+self.sid}
        response, content = self.h.request(self.reader_prep_uri, 'GET', body=None, headers=headers)
        #print response, content
        self.token = response
        return
        
    def feeds_content(self, feed, count=None):
        headers = {'Cookie': 'SID=%s; T=%s'%(self.sid, self.token)}
        if count:
            response, content = self.h.request(self.gfeed_limited%(feed, count), 'GET', body=None, headers=headers)
        else:
            response, content = self.h.request(self.gfeed%(feed), 'GET', body=None, headers=headers)
        return content
        
    def feeds(self, feed, count=None):
        content = self.feeds_content(feed, count)
        xml = XML2Dict()
        r = xml.fromstring(content)
        #from pprint import pprint
        #pprint(r)
        print r.feed.title.value
        return r.feed.title.value.encode('utf-8', 'ignore'), r.feed.entry
    
    def saveToGAE(self, feed_name, title, url, content):
        gae_url = "http://ismth.appspot.com/rss/add/"
        #gae_url = "http://localhost:8080/rss/add/"
        result = self.send(gae_url, {'name': feed_name, 'title': title, 'url': url, 'content': content, } )
        if result:
            print title, 'saved!'
        else:
            print title, 'error!'
        
    def send(self, url, data, proxies=None):
        params = urllib.urlencode(data)
        nf = urllib.urlopen(url, data=params, proxies=proxies)
        if nf:
            return True
        return False
    
def test():
    feed = "http://blog.sina.com.cn/rss/skyinwell.xml"
    #feed = "http://feeds.feedburner.com/Betterexplained"
    #feed = "http://blog.ifeng.com/rss/1300174.xml"
    #feed = "http://feeds.feedburner.com/ruanyifeng"
    
    user = "PyGtalkRobot"
    passwd = "PyGtalkRobotByLdmiao"
    fc = feedconverter(user, passwd)
    title, feeds = fc.feeds(feed, 2000)
    
    f = open(u'skyinwell.html', 'w')
    
    
    style='''<style>
        * {font-family: Consolas; font-size: 16px;}
        .feed {margin: 0.8em 1em 0.8em 1em; border: thin solid gray;}
        .title {padding: 0.3em 0 0.3em 1em; background-color:gray; font-weight:bold; font-size: 20px; text-decoration:none;}
        .content {padding: 0 0 0 1em; }\n</style>\n'''
    
    f.write('<html>\n<head>\n<title>%s</title>\n%s\n</head>\n<body>\n'%(title.encode('utf-8', 'ignore'), style))
    
    idx = 1
    feeds = reversed(feeds)
    for feed in feeds:
        print '%03d:'%(idx), feed.title.value
        #print 'feed source:', feed.source['stream-id'].value
        #print 'feed content:', feed.summary.value
        f.write('<div class="feed">\n')
        pattern = '  <div class="%s">%s</div>\n'
        f.write('  <div class="title">%d. <a href="%s" target="_blank">%s</a></div>\n'%(idx, feed.link.href.encode('utf-8', 'ignore'), feed.title.value.encode('utf-8', 'ignore')))
        
        content = ''
        if feed.has_key('content'):
            content = feed.content.value
        elif feed.has_key('summary'):
            content = feed.summary.value
        content = content.encode('utf-8', 'ignore')
		
        f1 = open(u'%3d.html'%(idx), 'w')
        f1.write('<div class="content">%s</div>\n'%(content));
        f1.close()
		
        f.write('  <div class="content">%s</div>\n'%(content))
        f.write('</div>\n\n')
        f.flush()
        
        idx += 1
    f.write('</body></html>')
    f.close()
	
def saveFeedToGAE():
    feed = "http://blog.sina.com.cn/rss/skyinwell.xml"
    #feed = "http://feeds.feedburner.com/Betterexplained"
    #feed = "http://blog.ifeng.com/rss/1300174.xml"
    #feed = "http://feeds.feedburner.com/ruanyifeng"
    
    user = "PyGtalkRobot"
    passwd = "PyGtalkRobotByLdmiao"
    fc = feedconverter(user, passwd)
    feed_title, feeds = fc.feeds(feed, 2000)
    
    idx = 1
    feeds = reversed(feeds)
    for feed in feeds:
        
        url = feed.link.href.encode('utf-8', 'ignore')
        title = feed.title.value.encode('utf-8', 'ignore')
        
        content = ''
        if feed.has_key('content'):
            content = feed.content.value
        elif feed.has_key('summary'):
            content = feed.summary.value
        content = content.encode('utf-8', 'ignore')
        
        fc.saveToGAE('skyinwell', title, url, content)
        
        idx += 1
		
if __name__=='__main__':
    test()
	#saveFeedToGAE()

        