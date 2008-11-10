#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import os
import sys
import random
import time
import MySQLdb
import download
import codecs

db = None

def saveUnique_Lyrics():
    f = open("lyrics.txt","r")
    url = f.readline()
    lyrics_url_set = set()
    while(url):
        lyrics_url_set.add(url)
        url = f.readline()
    f.close()
    
    #lyrics_name_set = set()
    f = open("lyrics_unique.txt","w")
    for url in lyrics_url_set:
        f.write(url)
        #saveToDB(url)
        #break
    f.close()

def saveLyrics_To_DB():
    f = open("lyrics_unique.txt","r")
    index = 1
    line = f.readline()
    while line:
        line = line.strip()
        saveToDB(line)
        print str(index)+" : "+line
        index = index+1
        #break
        line = f.readline()
        
    f.close()

def getDB():
    global db
    if db is None:
        db=MySQLdb.connect(host="16.157.92.20",port=3306,user="lyrics",passwd="lyrics",db="lyrics",charset="utf8")
    return db

def closeDB():
    global db
    if(db):
        db.close()

def converFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')

def saveToDB(down_from):
    db=getDB()
    c=db.cursor()
    filename = download.getFileName(down_from)
    content = getContent("lyrics/"+filename)
    if content is None:
        print filename+" not exist!"
    else:
        content = converFromGB2312ToUTF8(content)
        if content.lower().find('</html>') != -1:
            content = None
            os.remove("lyrics/"+filename)
    
    down_from = converFromGB2312ToUTF8(down_from)

    try:
        sql = ""
        if content is None:
            sql = "INSERT INTO `lyrics_error`(`down_from`) values ('"+db.escape_string(down_from)+"')"
        else:
            sql = "INSERT INTO `lyrics`(`lyric`, `down_from`) values ('"+db.escape_string(content)+"', '"+db.escape_string(down_from)+"')"
        #print sql
        c.execute(sql)
        db.commit()
    except:
        pass
        
def getContent(path):
    try:
        f = open(path, "r")
        content = f.read()
        f.close()
    except:
        return None

    return content
    
def processMetaDataInDB():
    db=getDB()
    c=db.cursor()
    sql = "SELECT `id`, `down_from`, `lyric` FROM `lyrics` WHERE `title` IS NULL"
    c.execute(sql)
    index = 1
    row = c.fetchone()
    while row:
        lyrics_id = row[0]
        down_from = row[1]
        lyric = row[2]
        saveMetaDataToDB(lyrics_id, down_from, lyric)
        #saveAlbumToDB(lyrics_id, down_from, lyric)
        row = c.fetchone()
        index = index + 1

def saveAlbumToDB(lyrics_id, down_from, lyric):
    album = extractAlbum(down_from, lyric)
    db=getDB()
    c=db.cursor()
    album = converFromGB2312ToUTF8(album)
    #print singer, title
    sql = "UPDATE `lyrics` SET `album`= '"+db.escape_string(album)+"' WHERE `id`="+str(lyrics_id)
    c.execute(sql)
    db.commit()
    print str(lyrics_id) +" : "+album
    #return album


def saveMetaDataToDB(lyrics_id, down_from, lyric):
    title, singer, album = extractMetaData(down_from, lyric)
    db=getDB()
    c=db.cursor()
    title = converFromGB2312ToUTF8(title)
    singer = converFromGB2312ToUTF8(singer)
    album = converFromGB2312ToUTF8(album)
    #print singer, title
    sql = "UPDATE `lyrics` SET `title`= '"+db.escape_string(title)+"', `singer`='"+db.escape_string(singer)+"', `album`='"+db.escape_string(album)+"' WHERE `id`="+str(lyrics_id)
    c.execute(sql)
    db.commit()
    print str(lyrics_id) +" : "+ singer+", "+title+", "+album
    #return singer, title, album

def extractMetaData(down_from, lyric):
    filename = download.getFileName(down_from)
    filename = filename[0:filename.rfind('.')]
    singer = filename[(filename.rfind('-')+1):len(filename)]
    title = filename[0:filename.rfind('-')]
    album = extractAlbum(down_from, lyric)
    return title, singer, album
    
def extractAlbum(down_from, lyric):
    #print lyric
    album = ""
    matched_obj = re.match(""".*?\[al\:(.*?)\]""", lyric, re.IGNORECASE| re.MULTILINE| re.DOTALL| re.LOCALE| re.UNICODE)
    if matched_obj:
        album = matched_obj.group(1)
    return album

def getDownloadErrorUrl():
    db=getDB()
    c=db.cursor()
    sql = "SELECT `down_from` from `lyrics` WHERE `lyric`='' "
    c.execute(sql)
    index = 1
    f = open("download_error_url.txt", "w")
    row = c.fetchone()
    while row:
        down_from = converFromGB2312ToUTF8(row[0])
        print str(index)+" : "+down_from
        download.downloadOneLyric(down_from, True)
        f.write(down_from+"\n")
        row = c.fetchone()
        index = index + 1
    f.close()

if __name__=="__main__":
    #insert the new lyrics to DB
    saveUnique_Lyrics()
    saveLyrics_To_DB()
    
    #process the lyrics in DB
    processMetaDataInDB()
    
    
    #getDownloadErrorUrl()
