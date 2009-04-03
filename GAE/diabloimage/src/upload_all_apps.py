#coding:utf-8
import os, re
import app_config

app_ids = [
            ('ifashiontaste', ['ldmiao@gmail.com','zhaoyong04@gmail.com','northtree.nk@gmail.com']), 
            ('ifashionsecret', ['ldmiao@gmail.com']), 
            ('ifashionshow', ['ldmiao@gmail.com']),
            ('fashion-taste', ['ldmiao@gmail.com','wyanyan05@gmail.com']),
            ('fashion-secret', ['ldmiao@gmail.com']),
            ('fashion-show', ['ldmiao@gmail.com','ldy8182@gmail.com']),
            ('smthmm', ['ldmiao@gmail.com']),
            ('smth-bbs', ['ldmiao@gmail.com']),
            ('newsmth', ['ldmiao@gmail.com']),
        ]

def run_cmd(cmd):
    os.system(cmd)
    
def upload():
    print '********************************************************************************************'
    print 'Start uploading...'
    run_cmd('appcfg.py update .\\')
    print 'Done!'
    print '********************************************************************************************'

def upload_all_apps(apps):
    for (app_id, admin_emails) in apps:
        app_config.changToAPPID(app_id)
        app_config.setAdmin(admin_emails)
        upload()
    
if __name__ == '__main__':
    #app_ids = [('newsmth', ['ldmiao@gmail.com'])]
    upload_all_apps(app_ids)
    
