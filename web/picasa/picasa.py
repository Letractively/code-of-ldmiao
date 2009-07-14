#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, codecs
import urllib
import urllib2
import os
import sys
import random
import time
import md5

import gdata.photos.service
import gdata.media
import gdata.geo


class Picasa():
    def __init__(self, app_name, email, password):
        self.app_name = app_name
        self.email = email
        self.password = password
        self.gd_client = None

    def connect(self):
        print 'start to log in...'
        self.gd_client = gdata.photos.service.PhotosService()
        self.gd_client.email = self.email
        self.gd_client.password = self.password
        self.gd_client.source = self.app_name
        self.gd_client.ProgrammaticLogin()
        print 'logged in!'

    def checkConnection(self):
        if self.email is None or self.password is None or self.app_name is None:
            print "Incomplete account information, please check your input."
            return
        if self.gd_client is None:
            self.connect()

    def getAlbums(self):
        self.checkConnection()
        albums = self.gd_client.GetUserFeed()
        return albums.entry

    def getAlbumsByUserName(self, username):
        self.checkConnection()
        albums = self.gd_client.GetFeed('/data/feed/api/user/%s' % (username))
        return albums.entry

    def getAlbumByUserNameAndAlbumname(self, username, albumname):
        self.checkConnection()
        album = self.gd_client.GetFeed('/data/feed/api/user/%s/album/%s' % (username, albumname))
        return album

    def getAlbumInfo(self, album):
        #id, uid, photoNum, title, description, provider, cover, source
        #print repr(album)
        if isinstance(album, gdata.photos.AlbumEntry):
            cover = album.media.thumbnail[0].url
            description = album.summary.text
        if isinstance(album, gdata.photos.AlbumFeed):
            cover = album.icon.text
            description = album.subtitle.text
        #print "cover before: " + cover
        p = re.compile('/s[\d]*-c/')
        cover = p.sub('/s64-c/', cover)
        #cover = cover.replace('/s[\d]*-c/', '/s64-c/')
        #print "cover after: " + cover
        return album.gphoto_id.text, album.user.text, album.numphotos.text, album.title.text, description, album.nickname.text, cover, album.GetHtmlLink().href

    def getPhotosOfAlbumOfLoggedInUser(self, album):
        self.checkConnection()
        photos = self.gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % ('default', album.gphoto_id.text))
        return photos.entry

    def getPhotosByUsernameAndAlbumid(self, username, albumid):
        self.checkConnection()
        photos = self.gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (username, albumid))
        return photos.entry

    def getPhotosByUsernameAndAlbumname(self, username, albumname):
        self.checkConnection()
        photos = self.gd_client.GetFeed('/data/feed/api/user/%s/album/%s?kind=photo' % (username, albumname))
        return photos.entry

    def putAlbum(self, title, summary, access='unlist'):
        self.checkConnection()
        album = self.gd_client.InsertAlbum(title=title, summary=summary, access=access)
        album = self.gd_client.Put(album, album.GetEditLink().href, converter=gdata.photos.AlbumEntryFromString)
        return album

    def putPhoto(self, album, title, description, filename, content_type='image/jpeg'):
        self.checkConnection()
        album_url = '/data/feed/api/user/%s/albumid/%s' % ('default', album.gphoto_id.text)
        photo = self.gd_client.InsertPhotoSimple(album_url, title, description, filename, content_type=content_type)
        return photo

    def getPhotoInfo(self, photo):
        #id, albumid, title, description, fullpic, thumbnail
        fullpic = photo.content.src
        thumbnail = photo.media.thumbnail[0].url
        #fullpic = thumbnail.replace('/s72/', '/s800/')
        return photo.gphoto_id.text, photo.albumid.text, photo.title.text, photo.summary.text, fullpic, thumbnail

    def getUserNameAndAlbumNameFromPicasaLink(self, url):
        if not url.startswith('http://picasaweb.google.com'):
            #print "No Picasa Web Album Links!"
            return None, None
        if url.count('/') >= 3:
            username = url.split('/')[3]
        if url.count('/') >= 4:
            albumname = url.split('/')[4].split('#')[0]
        else:
            albumname = None
        #print username, albumname
        return username, albumname


    def getAlbumAndPicsFromUsernameAndAlbumname(self, username, albumname):
        self.checkConnection()
        album = self.getAlbumByUserNameAndAlbumname(username, albumname)
        if album is None:
            return None, None

        #albumid, uid, photoNum, title, description, provider, cover, source = self.getAlbumInfo(album)

        photos = album.entry
        return album, photos
        """
        for photo in photos:
            #print self.getPhotoInfo(photo)
            id, albumid, title, description, src, thumbnail = self.getPhotoInfo(photo)
        """

    def getAlbumAndPicsFromPicasaAlbumLink(self, url):
        username, albumname = self.getUserNameAndAlbumNameFromPicasaLink(url)
        if username is None or albumname is None:
            return None, None

        return username, albumname, self.getAlbumAndPicsFromUsernameAndAlbumname(username, albumname)

    def getAlbumsFromPicasaUserLink(self, url):
        username, albumname = self.getUserNameAndAlbumNameFromPicasaLink(url)
        if username is None:
            return None

        albums = self.getAlbumsByUserName(username)

        return username, albums

    def printAll(self):
        albums = self.getAlbums()
        for album in albums:
            albumid, uid, photoNum, title, description, provider, cover, source = self.getAlbumInfo(album)
            print albumid, uid, photoNum, title, description, provider, cover, source

            photos = self.getPhotos(album)
            for photo in photos:
                id, albumid, title, description, src, thumbnail = self.getPhotoInfo(photo)
                print id, albumid, title, description, src, thumbnail

# ###################################################################################################
def log(str):
    if str:
        str = str.strip()
        if str != '':
            f = codecs.open("log.log", "a", "utf-8" )
            f.write(str + u'\n')
            f.close()

# ###################################################################################################
proxies = None

def getContent(url):
    '''change space char into %20'''
    url = url.replace(" ", "%20")
    content = None
    test_time = 3
    #success = False
    #while(success == False):
    while(test_time > 0):
        try:
            filehandle = urllib.urlopen(url, proxies=proxies)
            content = filehandle.read()
            #success = True
            test_time = 0
        except:
            #success = False
            test_time = test_time - 1
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

def saveImage(dirname, img_url, img_name=None):
    print "download image:" + img_url

    if not existFile(dirname):
        try:
            print "Create dir: "+dirname
            os.mkdir(dirname)
        except:
            dirname = "images"
            if not existFile(dirname):
                print "Create dir: "+dirname
                os.mkdir(dirname)

    if img_name is None:
        image_md5 = compute_md5(img_url)
        img_path_name = dirname + "/" + image_md5 + ".jpg"
    else:
        img_path_name = dirname + "/" + img_name
        image_md5 = img_name

    if existFile(img_path_name):
        print "\033[31m File " + img_path_name + " already exists, pass~~ \033[0m"
        return image_md5

    content = getContent(img_url)
    
    try:
        f = open(img_path_name, "wb")
        f.write(content)
        f.close()
        print "\033[33m Image " + img_path_name + " SAVE! \033[0m"
    except:
        print "Error occured, pass~"

    return image_md5


# ###################################################################################################
if __name__ == "__main__":
    '''
    email = 'name@gmail.com'
    password = 'pass'
    app_name = 'test-app'

    picasa = Picasa(app_name, email, password)
    username, albums = picasa.getAlbumsFromPicasaUserLink('http://picasaweb.google.com/cabbage718')

    for album in albums:
        albumid, uid, photoNum, title, description, provider, cover, source = picasa.getAlbumInfo(album)
        print albumid, uid, photoNum, title, description, provider, cover, source
        photos = picasa.getPhotosByUsernameAndAlbumid(username, albumid)
        for photo in photos:
            id, albumid, title, description, src, thumbnail = picasa.getPhotoInfo(photo)
            print id, albumid, title, description, src#, thumbnail
            log(src)
    '''
    
    f = codecs.open('log.log', 'r', 'utf-8')
    line = f.readline()
    while line:
        url = line.strip()
        saveImage('cabbage718', url, url[url.rfind('/')+1:])
        line = f.readline()
    