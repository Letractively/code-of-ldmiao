#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import httplib
import os
import sys

proxyhost = "web-proxy.hpl.hp.com"
proxyport = "8088"

proxyhost = "beiwebcache2.core.hp.com"
proxyport = "8080"

#proxies = {'http': 'http://'+proxyhost+':'+proxyport}
#proxies = None

# Kb
minImageSize = 10

def __LINE__():
    import traceback
    return traceback.extract_stack()[-2][1]

def replaceIlegalChar(name):
    newname = name.replace("/","")
    newname = newname.replace("\\","")
    newname = newname.replace(":","")
    newname = newname.replace("<","")
    newname = newname.replace(">","")
    newname = newname.replace("|","")
    newname = newname.replace("?","")
    newname = newname.replace("*","")
    newname = newname.replace("\"","")
    return newname

def getLegalDirName(dirname):
    newdirname = replaceIlegalChar(dirname)
    newdirname = newdirname.replace(".","")
    return newdirname

def getLegalFileName(filename):
    return replaceIlegalChar(filename)

def getChineseFromURL(url_str):
    result = urllib.unquote_plus(url_str);
    try:
        result = unicode(result,"utf8").encode("cp936")
    except:
        pass
    return result

def getContentLength(url):
    if url:
        print url
        match_obj = re.match("http://(.*?)(/.*)", url)
        host = match_obj.group(1)
        file = match_obj.group(2)
        #print host, file
        if host!=None and file!=None:
            test_time = 3
            #success = False
            #while(success == False):
            while(test_time>0):
                try:
                    conn = None
                    if proxies:
                        conn = httplib.HTTPConnection(proxyhost, proxyport)
                        conn.request("HEAD", url)
                    else:
                        conn = httplib.HTTPConnection(host)
                        conn.request("HEAD", file)
                    
                    response = conn.getresponse()
                    size = response.getheader('Content-length')
                    return int(size)
                except:
                    #success = False
                    test_time = test_time-1
                    print "Get ContentLength from:<"+url+"> failed, " + str(test_time) + " times left~~~~"

    return 0

def getContent(url):
    content = None
    test_time = 3
    #success = False
    #while(success == False):
    while(test_time>0):
        try:
            filehandle = urllib.urlopen(url, proxies=proxies)
            content = filehandle.read()
            #success = True
            test_time = 0
        except:
            #success = False
            test_time = test_time-1
            print "Download failed, " + str(test_time) + " times left~~~~"
    return content

def getDirName(url):
    dirname = url[(url.rfind('/')+1):(len(url))]
    dirname = getChineseFromURL(dirname)
    if dirname == None:
        dirname = "images"
    return dirname

def existFile(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

def saveImage(dirname, filename, img_url):
    albumname = dirname;
    size = getContentLength(img_url)

    if size < minImageSize*1024:
        print "File size: "+ str(size/1024) + "K, Less than "+str(minImageSize)+"K, just pass~~~"
        return
        
    print "File size: "+ str(size/1024) + "K, start download......"


    dirname = "D:\\Documents\\Images\\" + "images"
    
    if not existFile(dirname):
        try:
            print "Create dir: "+dirname
            os.mkdir(dirname)
        except:
            dirname = "images"
            if not existFile(dirname):
                print "Create dir: "+dirname
                os.mkdir(dirname)

    img_path_name = dirname+"/["+albumname+"]_["+str(size)+"]_"+filename
    if existFile(img_path_name):
        print "File "+img_path_name+" already exists, pass~~"
        return

    content = getContent(img_url)
    try:
        f = open(img_path_name,"wb")
        f.write(content)
        f.close()
        
        f = open("img_urls.txt", "a")
        f.write(img_url+"\n")
        f.close()
    except:
        print "Error occured, pass~"

def downloadAlbum(url, dirname=None):

    if dirname==None:
        dirname = getDirName(url)

    dirname = getChineseFromURL(dirname)
    dirname = getLegalDirName(dirname)

    matchstr = getContent(url)

    matched_groups = re.findall('s:"(.*?)"', matchstr)
    for matched in matched_groups:
        url = re.sub("\\\\x2F",'/', matched)
        newurl = re.sub("/s144/",'/', url)
        print newurl

        filename = newurl[(newurl.rfind('/')+1):(len(newurl))]
        filename = getChineseFromURL(filename)
        filename = getLegalFileName(filename)
        #print filename

        saveImage(dirname, filename, newurl+"?imgdl=1")


def downloadPersonAlbum(url):
    if url:
        username = url[(url.rfind('/')+1):(len(url))]

        content = getContent(url)

        matched_albumID2Name = re.findall('id:"(.*?)",title:"(.*?)"', content)
        print matched_albumID2Name
        albumID2NameDict = dict()
        for album in matched_albumID2Name:
            print album[0], album[1]
            albumID2NameDict[album[0]]=getChineseFromURL(album[1])

        #print albumID2NameDict

        matched_albumURL2ID = re.findall('<a href="(http://.*?)".*? id="title_(.*?)">', content)
        #matched_set = set(matched_groups)
        #print matched_albumURL2ID
        
        for album in matched_albumURL2ID:
            print album[0], album[1]
            albumName=None
            try:
                albumName = albumID2NameDict[album[1]]
                albumName = username+"__"+albumName
            except:
                albumName = None
            print albumName
            print "Album: " + albumName +" <"+ album[0]+"> start ........"
            downloadAlbum(album[0], albumName)
            print "Album: " + albumName +" <"+ album[0]+"> end *******\n"

def writeToList(matched_list):
    f = open("picasa.lst","w")
    for matched in matched_list:
        f.write(matched+"\n")
    f.close


def getPersonHomeURLs(content):
    matched_groups = re.findall('link: "(http.*?)"', content)
    matched_list = list()
    for matched in matched_groups:
        if matched.find("?")==-1:
            url = re.sub("\\\\x2F",'/', matched)
            matched_list.append(url)
    return matched_list


def downloadPersons(url):
    if url==None:
        return
    matched_list = list()
    if url.startswith('http://'):
        content = getContent(url)
        matched_list = getPersonHomeURLs(content)
    else:
        f = open(url,"r")
        if url.endswith(".htm") or url.endswith(".html"):
            content = f.read()
            matched_list = getPersonHomeURLs(content)
        else:
            line=f.readline()
            while line:
                matched_list.append(line.strip("\n"))
                line=f.readline()
            #print matched_list
        f.close()

    writeToList(matched_list)
    for matched in matched_list:
        print matched
        downloadPersonAlbum(matched)

def writeBatFile(args):
    cmd = "python"
    for arg in args:
        cmd += " " + arg
    f = open("update.bat","w")
    f.write(cmd+"\n")
    f.close

    f = open("update.sh","w")
    f.write(cmd+"\n")
    f.close

if __name__ == "__main__":
    if len(sys.argv)<2:
        print "Usage: picasa.py <url or person_file>"
        downloadPersons("http://picasaweb.google.com/lh/favorites");
    else:
        writeBatFile(sys.argv)
        url = sys.argv[1]
        if url and url.startswith('http://'):
            print url
            if url.count("/")==4:
                print "xx"
                downloadAlbum(url)
            elif url.count("/")==3:
                downloadPersonAlbum(url)
                print "yy"
        else:
            print "start"
            downloadPersons(url)
            print "end!"

    print "\nDownload Complete!"
    print "^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ ^_^ "
