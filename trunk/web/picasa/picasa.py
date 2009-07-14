#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, codecs

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

def log(str):
    if str:
        str = str.strip()
        if str != '':
            f = codecs.open("log.log", "a", "utf-8" )
            f.write(str + u'\n')
            f.close()
    
# ###################################################################################################
if __name__ == "__main__":
    email = 'accountname@gmail.com'   
    password = 'password'
    app_name = 'test-app'
    
    picasa = Picasa(app_name, email, password)
    username, albums = picasa.getAlbumsFromPicasaUserLink('http://picasaweb.google.com/AsianGirls.ilove')
    
    for album in albums:
        albumid, uid, photoNum, title, description, provider, cover, source = picasa.getAlbumInfo(album)
        print albumid, uid, photoNum, title, description, provider, cover, source
        photos = picasa.getPhotosByUsernameAndAlbumid(username, albumid)
        for photo in photos:
            id, albumid, title, description, src, thumbnail = picasa.getPhotoInfo(photo)
            print id, albumid, title, description, src#, thumbnail
            log(src)
    
    '''
    album, photos = picasa.getAlbumAndPicsFromPicasaAlbumLink('http://picasaweb.google.com/AsianGirls.ilove/KoreaScooterRaceChampionshipLeeJiWooPart2')
    print album
    print photos
    '''