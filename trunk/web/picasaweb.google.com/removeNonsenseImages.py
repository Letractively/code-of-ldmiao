#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import traceback

def getFileSize(path):
    return os.stat(path)[6]

def removeFile(path, minSize, maxSize):
    fileSize = getFileSize(path)
    if fileSize<minSize or fileSize>maxSize:
        try:
            os.remove(path)
            print "remove:" + path + ", File Size:" + str(fileSize)
            return True
        except:
            #print "error:/-----------------------------------"
            #print traceback.format_exc()
            #print "error:-----------------------------------/"
            pass

def renameImgFile(path):
    lowerPath = path.rstrip().lower()
    if lowerPath.endswith('.dat') and not path.endswith('index.dat'):
        os.rename(path, path+'.jpg')
        print "rename: " + path + " to " + path+'.jpg'
        
    
def removeImagesInDir(path, minSize, maxSize):
    if os.path.isfile(path):
        lowerPath = path.rstrip().lower()
        renameImgFile(path)
        if lowerPath.endswith('.jpg') or lowerPath.endswith('.jpeg') or lowerPath.endswith('.png') or lowerPath.endswith('.gif')  or lowerPath.endswith('.bmp'):
            removeFile(path, minSize, maxSize)
    elif os.path.isdir(path):
        for cp in os.listdir(path):
            childPath = os.path.join(path, cp)
            removeImagesInDir(childPath, minSize, maxSize)
if __name__ == '__main__':
    #dirPath = "D:\Documents\Images\images\"
    dirPath = 'D:\\Documents\\ScrapBook\\data\\'
    #dirPath = "C:\Users\linde\Pictures\Downloaded Albums"
    #removeImagesInDir("./", 20000L, 20000000L)
    removeImagesInDir(dirPath, 40000L, 20000000L)
    if raw_input("Press any key to exit..."):
        pass
    