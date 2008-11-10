#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

import MySQLdb
from MySQLdb import cursors

import codecs

import md5
import time


##############################################################################################################################################################################################

def converFromGB2312ToUTF8(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('utf-8', 'ignore')

def getGB2312UnicodeString(onestr):
    newstr = onestr
    try:
        newstr = unicode(newstr, 'cp936', 'ignore')
    except:
        pass
    return newstr.encode('cp936', 'ignore')

##############################################################################################################################################################################################
db = None

def getNewDB():
    return MySQLdb.connect(host="hplcws1.hpl.hp.com",port=3306,user="smth",passwd="smth",db="smth",charset="utf8")

def getDB():
    global db
    if db is None:
        db = getNewDB()
    return db

def closeDB():
    global db
    if(db):
        db.close()

#Format String in sql
def fs(onestr):
    db=getDB()
    return db.escape_string(converFromGB2312ToUTF8(onestr))



##############################################################################################################################################################################################

def cleanArcicleContent(content):
    newcontent = content
    newcontent = newcontent.replace("\\n", "\n")
    newcontent = newcontent.replace("\\'", "'")
    newcontent = newcontent.replace("\\\"", "\"")
    newcontent = newcontent.replace("\\\\", "\\")
    newcontent = newcontent.replace("\\/", "/")
    newcontent = re.sub("\\\\r\[\\d*?(;\\d*?)*?[a-zA-Z]", "", newcontent)
    return newcontent

def getSignature(content):
    match_obj = re.search("""^--\\n(.*?)^[^\\n]*?\\[FROM\\:\\s*?\\d*?\\.\\d*?\\.\\d*?\\..*?\\]""", content, re.MULTILINE | re.DOTALL)
    if match_obj:
        return match_obj.group(1)
    return ""

def getCleanText(content):
    
    #remove signature
    match_obj = re.compile("""^--\\n.*^[^\\n]*?\\[FROM\\:\\s*?\\d*?\\.\\d*?\\.\\d*?\\..*?\\]""", re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)
    
    content = content.encode('cp936', 'ignore')
    #print content
    
    #remove the title
    match_obj = re.compile(getGB2312UnicodeString("""^发信人.*?^发信站.*?站内\\n"""), re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)
        
    
    #remove the reference article
    match_obj = re.compile(getGB2312UnicodeString("""^(【 在.*? 的大作中提到.*?】\\n((\\:.*?\n)|(\\n))*)|^(\\:.*?\\n)"""), re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)

    #remove the reference board
    match_obj = re.compile(getGB2312UnicodeString("""^【 以下文字转载自.*? 讨论区 】\\n"""), re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)
        
    #remove blank line
    match_obj = re.compile(getGB2312UnicodeString("""^\\n"""), re.MULTILINE | re.DOTALL)
    if match_obj:
        content = match_obj.sub("", content)
       
    return content

##############################################################################################################################################################################################


def processArticles():
    db=getDB()
    c=db.cursor(cursors.SSCursor)
    sql = "SELECT `auto_increment_id`, `user_name`, `board_id`, `article_id`, `pub_time`, `content` FROM `article`"
    print sql
    c.execute(sql)
    row = c.fetchone()
    
    db1 = getNewDB()
    while row:
        #print "---------------------------------------------------------------------------------"
        print row[0]
        
        pub_time_str = row[4].strftime("%Y-%m-%d %H:%M:%S")

        article_md5 = row[1]+"_"+str(row[2])+"_"+str(row[3])+"_"+pub_time_str
        
        #print getCleanText(row[1])
        sql1 = "UPDATE `article` SET `article_md5`='"+fs(article_md5)+"', `html`='' WHERE `auto_increment_id`="+str(row[0])
        #print sql1
        try:
            c1=db1.cursor()
            c1.execute(sql1)
            db1.commit()
        except:
            pass
        row = c.fetchone()
    closeDB()


##############################################################################################################################################################################################

if __name__=="__main__":
    processArticles()
    