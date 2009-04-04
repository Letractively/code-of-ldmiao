#coding:utf-8
import os, re

files = [
            ('app.yaml', r'application\:\s+(.*)'),
            ('methods.py', r'http\://(.*?).appspot.com/'),
            ('views/cooliris.html', r'http\://(.*?).appspot.com/'),
            ('views/rss.xml', r'http\://(.*?).appspot.com/'),
        ]

def changToAPPID(app_id):
    global files
    for (file, re_str) in files:
        print file, re_str
        f = open(file, 'r')
        file_content = f.read()
        f.close()
        
        #print file_content
        match = re.search(re_str, file_content)
        if match:
            print match.start(1), match.end(1), match.group(1)
            if str(match.group(1))!=app_id:
                file_content = file_content[:match.start(1)]+app_id+file_content[match.end(1):]
                f = open(file, 'w')
                f.write(file_content)
                f.close()

def setAdmin(admin_emails_set=['ldmiao@gmail.com']):
    file = 'admin.py'
    re_str = r'admin_emails\s+=\s+set\((.*)\)'
    print str(admin_emails_set)
    
    f = open(file, 'r')
    file_content = f.read()
    f.close()
    
    #print file_content
    match = re.search(re_str, file_content)
    if match:
        print match.start(1), match.end(1), match.group(1)
        file_content = file_content[:match.start(1)]+str(admin_emails_set)+file_content[match.end(1):]
        #print file_content
        f = open(file, 'w')
        f.write(file_content)
        f.close()
    
if __name__ == '__main__':
    changToAPPID('fashion-secret')
    setAdmin(['ldmiao@gmail.com','wyanyan05@gmail.com'])
    