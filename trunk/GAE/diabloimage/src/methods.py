#coding:utf-8
import logging

from models import Images, ImageBlob, Gallery
from google.appengine.api import memcache
from google.appengine.api import images
from getimageinfo import getImageInfo
from google.appengine.ext import db


rss_template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
        <title>GAE Images</title>
        <link>http://ifashionsecret.appspot.com/</link>
        <description>GAE Images</description>
        %s
</channel>
</rss>
"""
rss_item_template = """
        <item>
                <title>%s</title>
                <link>/image/%s/</link>
                <guid>img_%s/</guid>
                <media:thumbnail url="/s/%s/" />
                <media:content url="/image/%s/" type="image/jpeg" />
        </item>
"""

def get_rss_template():
    global rss_template
    return rss_template

def generateRSSItems(images):
    global rss_item_template
    rss_items = ""
    for image in images:
        image_id = image.key().id()
        rss_items += rss_item_template%(image_id,image_id,image_id,image_id,image_id)
    return rss_items

def prependToRSS(images):
    rss_string = generateRSSItems(images)
    rss = memcache.get("rss_content")
    if rss:
        rss = rss_string + rss
    else:
        rss = rss_string
    
    memcache.set("rss_content", rss)

def persistRSS():
    rss = memcache.get("rss_content")
    if rss:
        gallery = Gallery.all().order('-updated_at').get()
        if gallery is None:
            gallery = Gallery(name="all")
        gallery.xml = rss
        gallery.put()

def getRSSItemsString():
    rss = memcache.get("rss_content")
    if rss:
        return rss
    else:
        gallery = Gallery.all().order('-updated_at').get()
        if gallery:
            rss = gallery.xml
            memcache.set("rss_content", rss)
            return rss
    return ""
    

def addImage(mime,description,bf):
    'Add Image'
    image=Images(mime=mime,description=description)
    image.size=len(image.bf)
    image.filetype,image.width,image.height=getImageInfo(bf)
    image.put()
    
    imageblob = ImageBlob(image=image, bf=bf)
    imageblob.put()
    
    prependToRSS([image])
    
    return image

def addImage2(bf):
    image=Images()
    image.size=len(bf)
    image.filetype,image.width,image.height=getImageInfo(bf)
    if not image.filetype:return None
    image.mime=image.filetype
    image.put()
    
    imageblob = ImageBlob(image=image, bf=bf)
    imageblob.put()
    
    prependToRSS([image])
    
    return image

def getImage(id):
    id=int(id)
    return Images.get_by_id(id)

def getCrop(image):
    width = image.width
    height = image.height
    lx = 0.0
    ty = 0.0
    rx = 1.0
    by = 1.0
    
    if(width>height):
        ratio = float(float(width)/height - 1)/2
        lx = ratio
        rx = 1.0 - ratio
    elif(height>width):
        ratio = float(float(height)/width - 1)/2
        ty = ratio
        by = 1.0 - ratio
    
    return lx, ty, rx, by

def getResize(image, max_len=240):
    width = image.width
    height = image.height
    
    w = max_len
    h = max_len
    
    if(width>height):
        ratio = float(width)/height
        w = max_len
        h = int(max_len/ratio)
    elif(height>width):
        ratio = float(height)/width
        h = max_len
        w = int(max_len/ratio)
    
    return w, h
    
def resizeImage(id,size="image"):
    image=getImage(id)
    if not image:return None
    
    imageblob = db.GqlQuery("SELECT * FROM ImageBlob WHERE image = :1", image).get()
    image.bf = imageblob.bf
    
    if size=="image":return image
    
    img=images.Image(image.bf)
    
    #lx, ty, rx, by = getCrop(image)
    #logging.info(str(lx) +","+ str(ty) +","+ str(rx) +","+ str(by))
    #img.crop(lx, ty, rx, by);
    
    width, height = getResize(image, 110)
    #logging.info(str(width) +","+ str(height))
    img.resize(width, height)
    
    img.im_feeling_lucky()
    image.bf=img.execute_transforms(output_encoding=images.JPEG)
    return image

def downImage(id,size="image"):
    key=id+size
    image=memcache.get(key)
    if not image:
        image=resizeImage(id, size)
        memcache.set(key,image,3600*24)
    return image

def delImage(key):
    image=Images.get(key)
    if image:
        imageblob = db.GqlQuery("SELECT * FROM ImageBlob WHERE image = :1", image).get()
        if imageblob:
            imageblob.delete()
        image.delete()

def delImageByid(id):
    image=Images.get_by_id(int(id))
    if image:
        imageblob = db.GqlQuery("SELECT * FROM ImageBlob WHERE image = :1", image).get()
        if imageblob:
            imageblob.delete()
        image.delete()

def getAllImages(index=0):
    return Images.all().order('-created_at').fetch(49, index*48)

def getImages(count=100, offset=0):
    return Images.all().order('-created_at').fetch(count, offset)
    
def getImagesBefore(count=100, lastImage_date=None):
    if lastImage_date:
        return db.GqlQuery("SELECT * FROM Images WHERE created_at < :1 ORDER BY created_at DESC", lastImage_date).fetch(count)
    else:
        return Images.all().order('-created_at').fetch(count)
    
def getPageing(index,page=0):
    s="/%s/"
    if page==0:
        if index==49:return (None,"/1/")
        else:return (None,None)
    if index==49:
        return ("/",s%(page+1)) if page==1 else (s %(page-1),s%(page+1))
    return ("/",None) if page==1 else (s %(page-1),None)
    