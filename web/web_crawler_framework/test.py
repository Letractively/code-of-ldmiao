from xml.dom import minidom
import inspect

dom = minidom.parse('conf.xml')
print dom.documentElement.tagName

for node in dom.documentElement.childNodes:
    if node.nodeType == 1:
        print node.nodeName

'''
for (name, value) in inspect.getmembers(minidom):
    #print name,':', value
    if inspect.isfunction(value):
        print name, value
'''