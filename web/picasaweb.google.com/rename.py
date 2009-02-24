import os

def renameImagesInDir(path):
    if os.path.isfile(path):
        lowerPath = path.rstrip().lower()
        if lowerPath.endswith('.bak'):
            os.rename(path, path.rstrip()+'.jpg')
    elif os.path.isdir(path):
        for cp in os.listdir(path):
            childPath = os.path.join(path, cp)
            renameImagesInDir(childPath)

if __name__ == '__main__':
    #dirPath = "D:\Documents\Images\images"
    dirPath = "D:\Documents\ScrapBook\data"
    #dirPath = "C:\Users\linde\Pictures\Downloaded Albums"
    renameImagesInDir(dirPath)
    if raw_input("Press any key to exit..."):
        pass