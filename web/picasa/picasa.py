#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

import gdata.photos.service
import gdata.media
import gdata.geo


class Picasa():
    def __init__(self, app_name, email, password, username='default'):
        self.app_name = app_name
        self.email = email
        self.password = password
        self.username = username
        
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
    
    def getPhotos(self, album):
        self.checkConnection()
        photos = self.gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (self.username, album.gphoto_id.text))
        return photos.entry

    def getPhotosByID(self, username, albumid):
        self.checkConnection()
        photos = self.gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (username, albumid))
        return photos.entry

    def getPhotosByName(self, username, albumname):
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
        album_url = '/data/feed/api/user/%s/albumid/%s' % (self.username, album.gphoto_id.text)
        photo = self.gd_client.InsertPhotoSimple(album_url, title, description, filename, content_type=content_type)
        return photo
        
    def getPhotoInfo(self, photo):
        #id, albumid, title, description, fullpic, thumbnail
        #fullpic = photo.content.src
        thumbnail = photo.media.thumbnail[0].url
        fullpic = thumbnail.replace('/s72/', '/s800/')
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
        
        return self.getAlbumAndPicsFromUsernameAndAlbumname(username, albumname)
    
    def getAlbumsFromPicasaUserLink(self, url):
        username, albumname = self.getUserNameAndAlbumNameFromPicasaLink(url)
        if username is None:
            return None
        
        albums = self.getAlbumsByUserName(username)
        
        return albums
        
    def printAll(self):
        albums = self.getAlbums()
        for album in albums:
            id, title, photoNum = self.getAlbumInfo(album)
            print id, title, photoNum
            
            photos = self.getPhotos(album)
            for photo in photos:
                id, albumid, title, src, thumbnails = self.getPhotoInfo(photo)
                print id, albumid, title, src #, thumbnails
                
    
