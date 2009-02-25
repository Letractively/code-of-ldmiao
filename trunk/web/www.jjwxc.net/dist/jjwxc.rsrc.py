{'application':{'type':'Application',
          'name':'Template',
    'backgrounds': [
    {'type':'Background',
          'name':'jjwxc',
          'title':u'\u664b\u6c5f\u6587\u5b66\u57ce\u5c0f\u8bf4\u4e0b\u8f7d',
          'size':(616, 559),
          'icon':'icon.ico',

         'components': [

{'type':'StaticText', 
    'name':'StaticText1', 
    'position':(14, 64), 
    'font':{'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 9}, 
    'foregroundColor':(255, 0, 0), 
    'text':u'\u6bcf\u884c\u4e00\u4e2a\u94fe\u63a5', 
    },

{'type':'TextArea', 
    'name':'novellinks', 
    'position':(88, 7), 
    'size':(512, 124), 
    'text':u'http://www.jjwxc.net/onebook.php?novelid=118426\nhttp://www.jjwxc.net/onebook.php?novelid=67918\nhttp://www.jjwxc.net/onebook.php?novelid=112926', 
    },

{'type':'TextArea', 
    'name':'log', 
    'position':(7, 202), 
    'size':(593, 303), 
    'editable':False, 
    },

{'type':'StaticText', 
    'name':'processpercent', 
    'position':(562, 173), 
    'size':(34, 16), 
    'alignment':u'right', 
    'text':u'0%', 
    },

{'type':'Gauge', 
    'name':'processgauge', 
    'position':(85, 169), 
    'size':(468, 23), 
    'layout':'horizontal', 
    'max':100, 
    'value':0, 
    },

{'type':'Button', 
    'name':'filechooser', 
    'position':(537, 139), 
    'size':(61, -1), 
    'label':u'\u6d4f\u89c8...', 
    },

{'type':'TextField', 
    'name':'savedir', 
    'position':(87, 140), 
    'size':(443, -1), 
    },

{'type':'StaticText', 
    'name':'statictext1', 
    'position':(17, 142), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 9}, 
    'text':u'\u4fdd\u5b58\u8def\u5f84', 
    },

{'type':'Button', 
    'name':'okbutton', 
    'position':(7, 167), 
    'size':(71, 28), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 9}, 
    'foregroundColor':(0, 0, 255), 
    'label':u'\u5f00\u59cb\u4e0b\u8f7d', 
    },

{'type':'StaticText', 
    'name':'firstchap', 
    'position':(15, 44), 
    'font':{'style': 'bold', 'faceName': u'Tahoma', 'family': 'sansSerif', 'size': 9}, 
    'text':u'\u5c0f\u8bf4\u94fe\u63a5', 
    },

] # end components
} # end background
] # end backgrounds
} }
