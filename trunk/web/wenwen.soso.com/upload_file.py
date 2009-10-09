#!/usr/bin/python
# -*- coding: utf-8 -*-

import MultipartPostHandler
import urllib2
import sys

params = {
'formids': 'pic',
'submitmode':'submit',
'submitname':'',
"pic" : open('fixit.jpg', "rb"),
}
validatorURL = "http://wenwen.soso.com/z/UploadPicNew3,uploadPic.d"
opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
print opener.open(validatorURL, params).read()