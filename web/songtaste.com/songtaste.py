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
def getContent(url, proxies = None):
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
            print "           -> Get:["+url+"] failed, " + str(test_time) + " times left~"
            time.sleep(random.randrange(8,12,1))
    return content

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

#--------------------------------------------------------------------------------------
def getSong(song_id, order, save_path):
    global proxy

    url = 'http://songtaste.com/play.php?song_id='+song_id
    htmlcontent = getContent(url, proxy)
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
    file_name = song_name.replace('\\','')
    file_name = file_name.replace('/', '')
    file_name = file_name.replace(':', '-')
    file_name = file_name.replace('*', '-')
    file_name = file_name.replace('?', '-')
    file_name = file_name.replace('"', '-')
    file_name = file_name.replace('<', '-')
    file_name = file_name.replace('>', '-')
    file_name = file_name.replace('|', '-')
    song_save_path = save_path+'/'+"%03d"%order+'_'+song_id+'_'+file_name+song_url[song_url.rfind('.'):]

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
    content = getContent(song_url, proxy)
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

    htmlcontent = getContent(url, proxy)
    getSongsFromHTML(htmlcontent, save_path)
    
#--------------------------------------------------------------------------------------
def getAllRecommendedSongsFromUserURL(url, save_path):
    global proxy
    global host
    
    htmlcontent = getContent(url, proxy)

    matched_groups = re.findall('''<a href='(/user/\d+/allrec/\d+)'>(\d+)</a>''', htmlcontent)
    for matched in matched_groups:
        url = host+matched[0].strip()
        htmlcontent += getContent(url, proxy)
    
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
    getAllRecommendedSongsFromUser('232464')
    #getSongsFromAblum('136560')
    #getSongsFromURL('http://songtaste.com/music/chart', 'week_order');
    #getSongsFromURL('http://songtaste.com/music.php?tag=chart&dt=2008-10-27', 'week_2008-10-27');
    #getSongsFromURL('http://songtaste.com/music/lsn', 'lsn');

