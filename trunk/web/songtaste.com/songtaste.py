#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import urllib
import urllib2
import os
import sys
import random
import time

import codecs
import traceback

from threadpool import ThreadPool


#--------------------------------------------------------------------------------------
#Configuraion

host = 'http://songtaste.com'

#proxy = {'http': 'http://beiwebcache1.core.hp.com:8080'}
proxy = None

thread_count = 5


#--------------------------------------------------------------------------------------

#get the HTML Source from url through proxies
def getContent(url, data=None, proxies=None):
    
    std_headers = {	
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
        'Accept-Language': 'en-us,en;q=0.5',
    }
    '''
    if proxies==None:
        print "           -> Get:["+url+"]"
    else:
        print "           -> Get:["+url+"] through " + proxies['http']
    '''

    content = None
    test_time = 3
    #success = False
    #while(success == False):
    while(test_time>0):
        try:
            if data:
                data = urllib.urlencode(data)
            if proxies is not None:
                proxy_support = urllib2.ProxyHandler(proxies)
                opener = urllib2.build_opener(proxy_support)
                urllib2.install_opener(opener)
            
            request = urllib2.Request(url, data, std_headers)
            response = urllib2.urlopen(request)
            content = response.read()
            
            #print content
            #success = True
            test_time = 0
        except urllib2.HTTPError, e:
            #print 'The server couldn\'t fullfill the request. Error code: ', e.code
            print "           -> Get:["+url+"] failed, Error code:", e.code
            content = None
            break
        except urllib2.URLError, e:
            #print 'We failed to reach a server. Reason: ', e.reason
            print "           -> Get:["+url+"] failed, Reason:", e.reason
            content = None
            break
        except:
            #success = False
            test_time = test_time-1
            print "           -> Get:["+url+"] failed, " + str(test_time) + " times left~"
            time.sleep(random.randrange(8, 12, 1))
        
    return content

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

#--------------------------------------------------------------------------------------
def getSong(song_id, order, save_path):
    global proxy
    global host
    
    url = host + '/play.php?song_id='+song_id
    htmlcontent = getContent(url, None, proxy)
    match_obj = re.search('''WrtSongLine\("(\d+)", "(.*?)\s*", ".*?", "\d*", "\d*", "(.*?)"\);''', htmlcontent)

    if not match_obj:
        return

    song_id = match_obj.group(1).strip()
    song_name = match_obj.group(2).strip()
    song_url = match_obj.group(3).strip()
    #print " ", song_id, song_name, song_url

    try:
        saveSong(order, song_id, song_name, song_url, save_path)
    except:
        print traceback.format_exc()

def getSongThread(data):
    getSong(data[0], data[1], data[2])


def saveSong(order, song_id, song_name, song_url, save_path):
    global proxy
    order = int(order)
    
    #--------------------------------------------------------------------------
    #Replace all the invalid characters
    #re.sub('''[\\\\/\:\*\?"<>\|]+''', '-', '\\,/,|,",:,*,?,<,>')
    #re.sub('''[\\\\/\:\*\?"<>\|]+''', '-', '\\/|":*?<>')
    #Replace '\' and '/' to empty string ''
    song_name = re.sub('''[\\\\/]+''', '', song_name)
    #Replace ':', '*', '?', '"', '<', '>', '|' to string '-'
    song_name = re.sub('''[\:\*\?"<>\|]+''', '-', song_name)
    song_name = song_name.strip()
    #--------------------------------------------------------------------------
    
    song_save_path = save_path+'/'+"%03d"%order+'_'+song_id+'_'+song_name+song_url[song_url.rfind('.'):]

    if not os.path.isdir(save_path):
        if existFile(save_path):
            print "  Path:["+ save_path+ "] is not a directory, exit!\n"
            return
        else:
            os.makedirs(save_path)

    if existFile(song_save_path):
        print "%03d"%order, "- File:[" + song_save_path+ "] already exists, pass.\n"
        return

    print "%03d"%order, '- Downloading:[' + song_save_path + '] \n           - From:[' + song_url+']'
    content = getContent(song_url, None, proxy)
    if content:
        print "%03d"%order, "- File  Saved:[" + song_save_path + "]"
        f = open(song_save_path,"wb")
        f.write(content)
        f.close()
    else:
        print "%03d"%order, "- Failed  for:[" + song_save_path + "]"
    print ""

#--------------------------------------------------------------------------------------
def getSongsFromHTML(htmlcontent, save_path):
    global thread_count

    pool = ThreadPool(thread_count)

    matched_groups = re.findall('''W[LS]\("(\d+)",\s*"(\d+)",\s*"(.*?)\s+",''', htmlcontent)
    for matched in matched_groups:
        print '-'*2 ,matched
        order = matched[0].strip()
        song_id = matched[1].strip()
        song_name = matched[2].strip()
        #getSong(song_id, order, save_path)
        pool.queueTask(getSongThread, (song_id, order, save_path))

    pool.joinAll()

def getSongsFromURL(url, save_path):
    global proxy

    htmlcontent = getContent(url, None, proxy)
    getSongsFromHTML(htmlcontent, save_path)
    
#--------------------------------------------------------------------------------------
def getAllRecommendedSongsFromUserURL(url, save_path):
    global proxy
    global host
    
    htmlcontent = getContent(url, None, proxy)

    matched_groups = re.findall('''<a href='(/user/\d+/allrec/\d+)'>(\d+)</a>''', htmlcontent)
    for matched in matched_groups:
        url = host+matched[0].strip()
        htmlcontent += getContent(url, None, proxy)
    
    getSongsFromHTML(htmlcontent, save_path)

def getAllRecommendedSongsFromUser(user_id):
    global host
    url = host+'/user/'+str(user_id)+'/allrec'
    getAllRecommendedSongsFromUserURL(url, 'user_'+str(user_id))

#--------------------------------------------------------------------------------------
def getSongsFromAblum(album_id):
    global host
    
    url = host+'/album/'+str(album_id)
    getSongsFromURL(url, 'album_'+str(album_id))

#--------------------------------------------------------------------------------------
if __name__=="__main__":
    #getAllRecommendedSongsFromUser('572763')
    #getSongsFromAblum('136560')
    #getSongsFromURL('http://songtaste.com/music/chart', 'week_order_new');
    #getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-05-11', 'week_2009-05-11')
    getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-06-01', 'week_2009-06-01')
    getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-06-08', 'week_2009-06-08')
    getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-06-15', 'week_2009-06-15')
    #getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-04-06', 'week_2009-04-06')
    #getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-02-16', 'week_2009-02-16')
    #getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-02-09', 'week_2009-02-09')
    #getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2009-02-02', 'week_2009-02-02')
    #getSongsFromURL('http://songtaste.com/music/lsn', 'lsn');
