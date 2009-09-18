import sys, re, traceback, codecs
import httplib2
import urllib, urllib2
from xml2dict import XML2Dict

feed_idx = 1

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
        
        
        global feed_idx
        f1 = open(u'feeds/feed_%02d.xml'%(feed_idx), 'w')
        feed_idx += 1;
        f1.write(content)
        f1.close()
		
        
        xml = XML2Dict()
        r = xml.fromstring(content)
        #from pprint import pprint
        #pprint(r)
        #print r.feed.title.value
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
    #feed = "http://blog.sina.com.cn/rss/gongzicaosan.xml"
    #feed = "http://xieguozhong.blog.sohu.com/rss"
    #feed = "http://blog.sina.com.cn/rss/jsmedia.xml"
    #feed = "http://yuanjian.blog.sohu.com/rss"
    feed = "http://xuxiaonian.blog.sohu.com/rss"
    feed = "http://lidaokui.blog.sohu.com/rss"
    feed = "http://fangang.blog.sohu.com/rss"
    feed = "http://blog.xuite.net/netmecc/mj/rss.xml"
    
    user = "PyGtalkRobot"
    passwd = "PyGtalkRobotByLdmiao"
    fc = feedconverter(user, passwd)
    title, feeds = fc.feeds(feed, 3000)
    
    f = open(u'mm.html', 'w')
    
    
    style='''<style>
        * {font-family: Consolas; font-size: 16px;}
        .feed {margin: 0.8em 1em 0.8em 1em; border: thin solid gray;}
        .title {padding: 0.3em 0 0.3em 1em; background-color:gray; font-weight:bold; font-size: 20px; text-decoration:none;}
        .content {padding: 0 0 0 1em; }\n</style>\n'''
        
    title = unicode(title, 'gbk', 'ignore').encode('utf-8', 'ignore')
    html_pre = '<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<title>%s</title>\n%s\n</head>\n<body>\n'%(title, style)
    
    f.write(html_pre)
    
    idx = 1
    feeds = reversed(feeds)
    for feed in feeds:
        print '%03d:'%(idx), feed.title.value
        #print 'feed source:', feed.source['stream-id'].value
        #print 'feed content:', feed.summary.value
        feed_pre = '<div class="feed">\n'
        feed_pre += '  <div class="title">%d. <a href="%s" target="_blank">%s</a></div>\n'%(idx, feed.link.href.encode('utf-8', 'ignore'), feed.title.value.encode('utf-8', 'ignore'))
        f.write(feed_pre)
        
        content = ''
        if feed.has_key('content'):
            content = feed.content.value
        elif feed.has_key('summary'):
            content = feed.summary.value
        content = content.encode('utf-8', 'ignore')
		
        '''
        f1 = open(u'skyinwell/%03d.html'%(idx), 'w')
        f1.write(html_pre)
        f1.write(feed_pre)
        f1.write('<div class="content">%s</div>\n'%(content));
        f1.write('</div>\n\n')
        f1.write('</body></html>')
        f1.close()
		'''
        
        f.write('  <div class="content">%s</div>\n'%(content))
        f.write('</div>\n\n')
        f.flush()
        
        idx += 1
    f.write('</body></html>')
    f.close()

def getFileName(name):
    #--------------------------------------------------------------------------
    #Replace all the invalid characters
    #re.sub('''[\\\\/\:\*\?"<>\|]+''', '-', '\\,/,|,",:,*,?,<,>')
    #re.sub('''[\\\\/\:\*\?"<>\|]+''', '-', '\\/|":*?<>')
    #Replace '\' and '/' to empty string ''
    name = re.sub('''[\\\\/]+''', '_', name)
    #Replace ':', '*', '?', '"', '<', '>', '|' to string '-'
    name = re.sub('''[\:\*\?"<>\|]+''', '-', name)
    name = name.strip()
    #--------------------------------------------------------------------------
    
    return name

def saveFeed(feedTitle, feed):
    #feed = "http://fangang.blog.sohu.com/rss"
    
    user = "PyGtalkRobot"
    passwd = "PyGtalkRobotByLdmiao"
    fc = feedconverter(user, passwd)
    title, feeds = fc.feeds(feed, 1000)
    
    #f = open(u'ldmiao\\%s.html'%(getFileName(feedTitle)), 'w')
    f = codecs.open(u'ldmiao\\%s.html'%(getFileName(feedTitle)), "w", "utf-8" )
    
    style=u'''<style>
        * {font-family: Consolas; font-size: 16px;}
        .feed {margin: 0.8em 1em 0.8em 1em; border: thin solid gray;}
        .title {padding: 0.3em 0 0.3em 1em; background-color:gray; font-weight:bold; font-size: 20px; text-decoration:none;}
        .content {padding: 0 0 0 1em; }\n</style>\n'''
        
    title = unicode(title, 'utf-8', 'ignore')
    html_pre = u'<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<title>%s</title>\n%s\n</head>\n<body>\n'%(title, style)
    
    f.write(html_pre)
    
    idx = len(feeds)
    #feeds = reversed(feeds)
    for feed in feeds:
        try:
            print '%03d:'%(idx), feed.title.value
            #print 'feed source:', feed.source['stream-id'].value
            #print 'feed content:', feed.summary.value
        except:
            pass
        feed_pre = u'<div class="feed">\n'
        feed_pre += u'  <div class="title">%d. <a href="%s" target="_blank">%s</a></div>\n'%(idx, feed.link.href, feed.title.value)
        f.write(feed_pre)
        
        content = u''
        if feed.has_key('content'):
            content = feed.content.value
        elif feed.has_key('summary'):
            content = feed.summary.value
        #content = content.encode('utf-8', 'ignore')
		
        '''
        f1 = open(u'skyinwell/%03d.html'%(idx), 'w')
        f1.write(html_pre)
        f1.write(feed_pre)
        f1.write('<div class="content">%s</div>\n'%(content));
        f1.write('</div>\n\n')
        f1.write('</body></html>')
        f1.close()
		'''
        
        f.write(u'  <div class="content">%s</div>\n'%(content))
        f.write(u'</div>\n\n')
        f.flush()
        
        idx -= 1
    f.write('</body></html>')
    f.close()
    
def archive():
    #f = open('google-reader-subscriptions.xml', 'r')
    f = codecs.open( "google-reader-subscriptions.xml", "r", "utf-8" )
    subscriptions=f.read()
    f.close()
    
    matched_groups = re.findall('''<outline\s+text="(.*?)"\s+title="(.*?)"\s+type="(.*?)"\s+xmlUrl="(.*?)"\s+htmlUrl="(.*?)"/>''', subscriptions)
    for matched in matched_groups:
        text = matched[0]
        title = matched[1]
        type = matched[2]
        xmlUrl = matched[3]
        htmlUrl = matched[4]
        print type, title.encode('gbk'), xmlUrl
        try:
            saveFeed(title, xmlUrl)
        except:
            print "Error:", xmlUrl
            print traceback.format_exc()

def saveFeedToGAE():
    feed = "http://blog.sina.com.cn/rss/skyinwell.xml"
    #feed = "http://feeds.feedburner.com/Betterexplained"
    #feed = "http://blog.ifeng.com/rss/1300174.xml"
    #feed = "http://feeds.feedburner.com/ruanyifeng"
    
    user = "PyGtalkRobot"
    passwd = "PyGtalkRobotByLdmiao"
    fc = feedconverter(user, passwd)
    feed_title, feeds = fc.feeds(feed, 8000)
    
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
    #archive()
    #saveFeed(u"mm", "http://blog.xuite.net/netmecc/mj/rss.xml")
        