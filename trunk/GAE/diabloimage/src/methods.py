#coding:utf-8
import logging

from models import Images
from google.appengine.api import memcache
from google.appengine.api import images
from getimageinfo import getImageInfo

def addImage(mime,description,bf):
    'Add Image'
    image=Images(mime=mime,description=description,bf=bf)
    image.size=len(image.bf)
    image.filetype,image.width,image.height=getImageInfo(bf)
    image.put()
    return image

def addImage2(bf):
    image=Images(bf=bf)
    image.size=len(bf)
    image.filetype,image.width,image.height=getImageInfo(bf)
    if not image.filetype:return None
    image.mime=image.filetype
    image.put()
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
    if image:image.delete()

def delImageByid(id):
    image=Images.get_by_id(int(id))
    if image:image.delete()

def getAllImages(index=0):
    return Images.all().order('-created_at').fetch(49, index*48)

def getImages(count=1000, offset=0):
    return Images.all().order('-created_at').fetch(count, offset)
    
def getPageing(index,page=0):
    s="/%s/"
    if page==0:
        if index==49:return (None,"/1/")
        else:return (None,None)
    if index==49:
        return ("/",s%(page+1)) if page==1 else (s %(page-1),s%(page+1))
    return ("/",None) if page==1 else (s %(page-1),None)
    