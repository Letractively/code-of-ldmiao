#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import os
import sys
import random
import time

#proxies = {'http': 'http://web-proxy.hpl.hp.com:8088'}
#proxies = {'http': 'http://atlwebcache.core.hp.com:8080'}
#proxies = {'http': 'http://beiwebcache2.core.hp.com:8080'}
#proxies = {'http': 'http://beiwebcache1.core.hp.com:8080'}

proxies = None

proxy_set = None

def getProxies():
    content = getContent('http://autocache.hp.com')
    f = open("autoproxy.txt", "w")
    f.write(content)
    f.close()
    matched_groups = re.findall('\WPROXY\s*?(.*?):(\d{1,})', content)
    print "Proxy List:"
    global proxy_set
    proxy_set = set()
    
    #proxy_set.add('http://web-proxy.hpl.hp.com:8088')
    #proxy_set.add('http://atlwebcache.core.hp.com:8080')
    proxy_set.add('http://beiwebcache2.core.hp.com:8080')
    proxy_set.add('http://beiwebcache1.core.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    
    #proxy_set.add('http://proxy.cce.cpqcorp.net:8080')
    #proxy_set.add('http://atlwebcache3.core.hp.com:8080')
    
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    #proxy_set.add('http://web-proxy.austin.hp.com:8080')
    
    for matched in matched_groups:
        print matched
        host = matched[0].strip()
        port = matched[1].strip()
        if host != 'localhost' and host != '131.168.229.119':
            proxy_set.add("http://"+host+":"+port)
            print host+":"+port
            
def getOneProxy():
    global proxy_set
    if(proxy_set==None):
        getProxies()
    if(proxy_set==None or len(proxy_set)==0):
        return None
    randm_num = random.randint(0, len(proxy_set)-1)
    i=0
    for proxy in proxy_set:
        if i==randm_num:
            return {"http" : proxy}
        i = i+1
    #return {'http': 'http://beiwebcache1.core.hp.com:8080'}

def getChineseFromURL(url_str):
    result = urllib.unquote_plus(url_str);
    try:
        result = unicode(result,"utf8").encode("cp936")
    except:
        pass
    return result


def getContent(url, proxies=None):
    if proxies==None:
        print "Download ---->"+url
    else:
        print "Download ---->"+url+" through " + proxies['http']
    content = ""
    test_time = 3
    #success = False
    #while(success == False):
    while(test_time>0):
        try:
            filehandle = None
            if proxies==None:
                filehandle = urllib.urlopen(url)
            else:
                filehandle = urllib.urlopen(url, proxies=proxies)
            content = filehandle.read()
            #print content
            #success = True
            test_time = 0
        except:
            #success = False
            test_time = test_time-1
            print "Download "+url+" failed, " + str(test_time) + " times left~~~~"
            time.sleep(1)
    return content


def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

def getPostResponse(url, values={}):
    
    proxy_support = urllib2.ProxyHandler(getOneProxy())
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)

    
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    values = {'name' : 'Michael Foord',
              'location' : 'Northampton',
              'language' : 'Python' }
    headers = { 'User-Agent' : user_agent }
    
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    
    return the_page
    
def getSingerURL():
    content = getContent('http://list.mp3.baidu.com/singer/singers.html?top7', getOneProxy())
    #print content
    matched_groups = re.findall('<a href="(\d{2}/.*?\.htm)"', content)
    print "Singer List:"
    singer_set = set()
    for matched in matched_groups:
        singer = "http://list.mp3.baidu.com/singer/"+matched.strip()
        singer_set.add(singer)
    
    f = open("singers.txt","w")
    for singer in singer_set:
        f.write(singer+"\n")
        print "yyyyy--->"+singer
    f.close
    
    return singer_set;


def getSingerPagesURL(singer_set):
    if singer_set != None:
        singer_url_set = set()
        f = open("singer_urls.txt","a")
        for singer in singer_set:
            singer_url, max_pn = getSingerPageCount(singer)
            url = None
            if singer_url==None and max_pn==0:
                url = singer
            else:
                url = singer_url+str(max_pn)
            f.write(url+"\n")
            f.flush()
            singer_url_set.add(url)
        f.close
        return singer_url_set


def getSingerPageCount(url, prev_max_pn=0):
    content = getContent(url, getOneProxy())
    matched_groups = re.findall('<a href=([^>]*?pn=)(\d{1,})>\[\d{1,}\]', content)
    max_pn = 0
    url_pre = None
    for matched in matched_groups:
        matched_pn = int(matched[1])
        if max_pn < matched_pn:
            max_pn = matched_pn
        if url_pre == None:
            url_pre = matched[0].strip()

    if max_pn > prev_max_pn:
        return getSingerPageCount(url_pre+str(max_pn), max_pn)
    else:
        if url_pre==None and prev_max_pn!=0:
            match_obj = re.match("([^>]*?pn=)\d{1,}", url)
            url_pre = match_obj.group(1)
            prev_max_pn = prev_max_pn-1*30
        return url_pre, prev_max_pn

def getSingerLyricsURL():
    f = open("singer_urls.txt","r")
    url = f.readline()
    while(url):
        lyrics_url_set = set()
        if(url.startswith('http://list.mp3.baidu.com')):
            addSingerLyricsToSet(lyrics_url_set, url)
        else:
            match_obj = re.match("([^>]*?pn=)(\d{1,})", url)
            url_pre = match_obj.group(1)
            max_pn = int(match_obj.group(2))
            i=0
            while(i<=max_pn):
                addSingerLyricsToSet(lyrics_url_set, url_pre+str(i))
                i=i+30
        for lyrics_url in lyrics_url_set:
            downloadLyrics(lyrics_url)
            
        url = f.readline()
    f.close()

def addSingerLyricsToSet(lyrics_url_set, url):
    content = getContent(url, getOneProxy())
    matched_groups = re.findall('<a href="(http://mp3.baidu.com/m\?tn=baidump3lyric.*?)"', content)
    for matched in matched_groups:
        lyrics_url_set.add(matched)

def downloadLyrics(url):
    content = getContent(url, getOneProxy())
    matched_groups = re.findall('<a href="(.*?\.lrc)"', content)
    f = open("lyrics.txt","a")
    for matched in matched_groups:
        #print matched
        f.write(matched+"\n")
        downloadOneLyric(matched)
    f.close()

def downloadOneLyric(url):
    print "->->"+url

if __name__=="__main__":
    #print getContent('http://autocache.hp.com')
    #print getContent('http://list.mp3.baidu.com/singer/singers.html?top7', getOneProxy())
    
    
    
    #print getSingerPageCount("http://list.mp3.baidu.com/singer/32/3236_simp3.htm")
    #print getSingerPageCount("http://list.mp3.baidu.com/singer/30/3038_simp3.htm")
    
    #singer_set = getSingerURL()
    #getSingerPagesURL(singer_set)
    
    getSingerLyricsURL()
