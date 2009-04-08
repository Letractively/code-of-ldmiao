#!/usr/bin/python
#coding=utf8

"""
getsong is a tool for downloading mp3 automatically, with getsong you can do-
wnload mp3 in a flash:)

Author: Xupeng Yun <recordus@gmail.com>, 2006

Usage:
    Download mp3 file which matches given artist and/or title.
      
      -h --help         show this help message.
      -d --songsdir     dir of your songs repo.
      -1 --100          download Baidu Top100 new songs. 
      -5 --500          download Biadu Top500 new songs.
      -a --artist       songer
      -t --title        song name
      -v --version      show version info
"""

import re
import os
import sys
import time
import glob
import string
import socket
import getopt
import urllib
import urllib2
import threading
from sgmllib import SGMLParser

#############################################################################
#
# self-defined exception classes
#
#############################################################################
class ConnectionError(Exception): pass
class URLUnreachable(Exception):pass
class CanotDownload(Exception):pass

#############################################################################
#
# multiple threads download module starts here
#
#############################################################################
class HttpGetThread(threading.Thread):
    def __init__(self, name, url, filename, range=0):
        threading.Thread.__init__(self, name=name)
        self.url = url
        self.filename = filename
        self.range = range
        self.totalLength = range[1] - range[0] +1
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0
        self.percent = self.downloaded/float(self.totalLength)*100
        self.headerrange = (self.range[0]+self.downloaded, self.range[1])
        self.bufferSize = 8192


    def run(self):
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0
        self.percent = self.downloaded/float(self.totalLength)*100
        #self.headerrange = (self.range[0]+self.downloaded, self.range[1])
        self.bufferSize = 8192
        #request = urllib2.Request(self.url)
        #request.add_header('Range', 'bytes=%d-%d' %self.headerrange)
        downloadAll = False
        retries = 1
        while not downloadAll:
            if retries > 10:
                break
            try: 
                self.headerrange = (self.range[0]+self.downloaded, self.range[1])
                request = urllib2.Request(self.url)
                request.add_header('Range', 'bytes=%d-%d' %self.headerrange)
                conn = urllib2.urlopen(request)
                startTime = time.time()
                data = conn.read(self.bufferSize)
                while data:
                    f = open(self.filename, 'ab')
                    f.write(data)
                    f.close()
                    self.time = int(time.time() - startTime)
                    self.downloaded += len(data)
                    self.percent = self.downloaded/float(self.totalLength) *100               
                    data = conn.read(self.bufferSize)
                downloadAll = True
            except Exception, err:
                retries += 1
                time.sleep(1)
                continue

def Split(size,blocks):
    ranges = []
    blocksize = size / blocks
    for i in xrange(blocks-1):
        ranges.append(( i*blocksize, i*blocksize+blocksize-1))
    ranges.append(( blocksize*(blocks-1), size-1))

    return ranges

def GetHttpFileSize(url):
    length = 0
    try:
        conn = urllib.urlopen(url)
        headers = conn.info().headers
        for header in headers:
            if header.find('Length') != -1:
                length = header.split(':')[-1].strip()
                length = int(length)
    except Exception, err:
        pass
        
    return length

def hasLive(ts):
    for t in ts:
        if t.isAlive():
            return True
    return False

def MyHttpGet(url, output=None, connections=4):
    """
    arguments:
        url, in GBK encoding
        output, default encoding, do no convertion
        connections, integer
    """
    length = GetHttpFileSize(url)
    mb = length/1024/1024.0
    if length == 0:
        raise URLUnreachable
    blocks = connections
    if output:
        filename = output
    else:
        output = url.split('/')[-1]
    ranges = Split(length, blocks)
    names = ["%s_%d" %(filename,i) for i in xrange(blocks)]
    
    ts = []
    for i in xrange(blocks):
        t = HttpGetThread(i, url, names[i], ranges[i])
        t.setDaemon(True)
        t.start()
        ts.append(t)

    live = hasLive(ts)
    startSize = sum([t.downloaded for t in ts])
    startTime = time.time()
    etime = 0
    while live:
        try:
            etime = time.time() - startTime
            d = sum([t.downloaded for t in ts])/float(length)*100
            downloadedThistime = sum([t.downloaded for t in ts])-startSize
            try:
                rate = downloadedThistime / float(etime)/1024
            except:
                rate = 100.0
            progressStr = u'\rFilesize: %d(%.2fM)  Downloaded: %.2f%%  Avg rate: %.1fKB/s' %(length, mb, d, rate)
            sys.stdout.write(progressStr)
            sys.stdout.flush()
            #sys.stdout.write('\b'*(len(progressStr)+1))
            live = hasLive(ts)
            time.sleep(0.2)
        except KeyboardInterrupt:
            print
            print "Exit..."
            for n in names:
                try:
                    os.remove(n)
                except:
                    pass
            sys.exit(1)
            
    print
    print  u'耗时： %d:%d, 平均速度：%.2fKB/s' %(int(etime)/60, int(etime)%60,rate) 

    f = open(filename, 'wb')
    for n in names:
        f.write(open(n,'rb').read())
        try:
            os.remove(n)
        except:
            pass
    f.close()

#############################################################################
#
# get artist-title pairs from baidu top songs list
#
#############################################################################
class SongParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.songs = {}
        self.cursong = ''
        self.insong = False
        self.newsong = False
        self.name = ''
        
    def handle_data(self, text):
        txt = text.strip()
        if txt == '':
            return
        res = re.search('^(\d{1,3})\.$', txt)
        if res:
            rank = int(res.groups()[0])
            self.cursong = rank
            self.songs[rank] = ''
            self.insong = True
            self.name = 'artist'
        else:
            if self.insong:                
                self.songs[self.cursong] = self.songs[self.cursong] + txt
                if txt == ')':
                    self.insong = False
   
def GetArtistAndTitle(url):
    html = urllib.urlopen(url).read()
    html = html.decode('gbk', 'ignore').encode('utf8')
    parser = SongParser()
    parser.feed(html)
    songs = parser.songs
    for k, v in songs.items():
        pos = v.find('(')
        if pos != -1:
            title = v[:pos]
            artist = v[pos+1:-1]
            artist = artist.replace('/', '_')
        else:
            title = v
            artist = ''
        artist = artist.decode('utf8', 'ignore')
        title = title.decode('utf8', 'ignore')
        info = {'artist':artist, 'title':title}
        songs[k] = info
        
    return songs    

#############################################################################
#
# mp3 download module starts here
#
#############################################################################
class URLChecker(threading.Thread):
    def __init__(self, fakeurl):
        threading.Thread.__init__(self, name='')
        self.etime = 0
        self.length = 0
        self.url = GetRealMp3URL(fakeurl)
        
    def run(self):
        if not self.url:
            self.etime = 200000
            return
        socket.setdefaulttimeout(10)
        try:
            start = time.time()
            conn = urllib2.urlopen(self.url)
            end = time.time()
            etime = int((end - start)*1000)
            info = conn.info()
            for header in info.headers:
                if 'Length' in header:
                    length = int(header.split(':')[-1])
            self.etime = etime
            self.length = length
            if self.length < 2*1024*1024:
                self.etime = 200000
        except Exception:
            self.etime = 200000
            self.length = 0

def GetBestUrl(urls):
    cthreads = []
    for url in urls:
        t = URLChecker(url)
        cthreads.append(t)
        t.start()
        
    live = hasLive(cthreads)
    while live:
        live = hasLive(cthreads)
        time.sleep(0.3)
    
    besturl = ''
    setime = 100000
    for t in cthreads:
        if t.etime < setime:
            besturl = t.url
            setime = t.etime
    
    return besturl
    
def QuoteURL(url):
    """
    arguments:
        url, in GBK encoding.
    return vlaues:
        url, in GBK encoding.
    """
    pattern = u'[\u4e00-\u9fa5]+'.encode('utf8')
    rs = re.findall(pattern, url.decode('gbk', 'ignore').encode('utf8'))
    for word in rs:
        url = url.replace(word, urllib.quote(word.decode('utf8', 'ignore').encode('gbk')))
    
    return url

def __getFakeURLs(artist, title):
    """Search results in baidu can't be downloaded directly,
       this function get top 30(or less) urls from the results.
       arguments:
           artist (unicode)
           title (unicode)
       return values:
           urls: urls got from search results, in GBK encoding.
    """
    baseurl = 'http://mp3.baidu.com/m?f=ms&tn=baidump3&ct=134217728&lf=&rn=&lm=0&word='
    #multi artist are seperated by '_', replace it with space here
    artist = artist.replace('_', ' ')
    keyword = '%s %s' %(artist, title)
    keyword = keyword.encode('gbk')
    url = baseurl + urllib.quote(keyword, string.punctuation)
    
    urls = []
    try:
        html = urllib2.urlopen(url).read()
    except UnicodeDecodeError:
        return urls
    except:
        return urls
    
    pattern = 'http://.*baidusg.*&lm=16777216'
    urls = re.findall(pattern, html)

    if len(urls) >= 20:
        return urls[:20]
    else:
        return urls

def GetRealMp3URL(fakeurl): 
    """
    arguments:
        fakeurl, in GBK encoding.
    return values:
        realurl, in GBK encoding.
    """
    p = 'baidusg,(.*)&word'
    ret = re.search(p, fakeurl)
    if ret:
        toreplaced = ret.groups()[0]
        fakeurl = fakeurl.replace(toreplaced, 'recordus')   
    url = QuoteURL(fakeurl)
    try:
        html = urllib.urlopen(url).read()
    
        pattern = 'http://.*\.(mp3|MP3|mP3|Mp3)'
        ret = re.search(pattern, html)
        if ret:
            realurl = ret.group()
        else:
            realurl = None
    except:
        realurl = None
    return realurl

#def CheckURL(url, timeout=10):
#    """Check remote file's size and access time.
#        arguments:
#            url: url to test.
#        return values:
#            return (length, etime)
#            length: remote file's size
#            etime: usecs used to get headers.
#    """
#    socket.setdefaulttimeout(timeout)
#    length = 0
#    etime = 15000
#    try:
#        start = time.time()
#        conn = urllib2.urlopen(url)
#        end = time.time()
#        etime = int((end - start)*1000)
#        info = conn.info()
#        for header in info.headers:
#            if header.find('Length') != -1:
#                length = int(header.split(':')[-1])
#    except:
#        raise ConnectionError
#    
#    return (length, etime)
    
def DownloadSong(artist, title, songsdir='/data/Mp3/Top100'):
    """
    arguments:
        artist (unicode)
        title (unicode)
        songdir (unicode)
    """
    filename = u'%s-%s.mp3' %(artist, title)
    if title == '':
        return
    if artist == '':
        filename = u'%s.mp3' %title
    filename = filename.encode(sys.getfilesystemencoding())
    songdir = songsdir.encode(sys.getfilesystemencoding())

    if os.path.exists(os.path.join(songsdir, filename)) or os.path.exists(filename):
        print u"已经成功下载《%s - %s》"%(artist, title)
        return
    
    print u"准备下载《%s - %s》..." %(artist, title)
    print u'正在选取最快的URL：'
    fakeurls = __getFakeURLs(artist, title)
    url = GetBestUrl(fakeurls)
    print url.decode('gbk', 'ignore')
    try:
        MyHttpGet(url, filename, 3)
    except URLUnreachable:
        print u"Sorry, 目前并没有为(%s - %s)找到合适的下载资源，\n您可以手动下载或稍候再试。" %(artist, title)
    except KeyboardInterrupt:
        print u'是我强行终止的。'


def DownloadTopSongs(type='100'):
    try:
        if type == '100':
            songs = GetArtistAndTitle('http://list.mp3.baidu.com/list/newhits.html?id=1#top1')
        elif type == '500':
            songs = GetArtistAndTitle('http://list.mp3.baidu.com/topso/mp3topsong.html?id=1#top2')
        for rank, info in songs.items():
            artist = info['artist']
            title = info['title']
            print
            print u"正在下载第%d首（共%d首) 歌手：%s 曲名：%s" %(rank, len(songs), artist, title)
            DownloadSong(artist, title)
    except KeyboardInterrupt:
        print "Exiting..."

def Help():
    helpstr = """Usage: %s [OPTION]
Download mp3 file which matches given artist and/or title.
  
  -h --help         show this help message.
  -d --songsdir     dir of your songs repo.
  -1 --100          download Baidu Top100 new songs. 
  -5 --500          download Biadu Top500 new songs.
  -a --artist       songer
  -t --title        song name
  -v --version      show version info
    """%sys.argv[0]
    print helpstr
    sys.exit(0)
    
if __name__ == "__main__":
    artist = ''
    titles = []
    songsdir='/data/Mp3/Top100'
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   '15hva:t:d:', 
                                   ['100','500','help', 'version', 'artist=','title=', 'songsdir=']
                                   )
    except getopt.GetoptError:
        Help()
        

    if len(opts) == 0:
        Help()

    for o, a in opts:
        if o in ('-h', '--help'):
            Help()
        if o in ('-d', '--songsdir'):
            songsdir = a
        if o in ('-a', '--artist'):
            artist = a
        if o in ('-t', '--title'):
            titles.append(a)
        if o in ('-1', '--100'):
            try:
                DownloadTopSongs('100')
            except KeyboardInterrupt, err:
                print '(Main)Exiting...'
                sys.exit(0)
            sys.exit(0)
        if o in ('-5', '--500'):
            DownloadTopSongs('500')
            sys.exit(0)
        if o in ('-v', '--version'):
            print 'v1.0 by Xupeng Yun <recordus@gmail.com>'
    for title in titles:
        title = title.decode(sys.stdin.encoding, 'ignore')
        artist = artist.decode(sys.stdin.encoding, 'ignore')
        DownloadSong(artist, title)
