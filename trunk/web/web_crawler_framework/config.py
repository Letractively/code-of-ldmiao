from xml.dom import minidom
import pprint

class ListPattern:
    name = None
    subPattern = None
    subURL = None
    nextPagePattern = None
    nextPageURL = None
    
    def __init__(self, name, subPattern, subURL, nextPagePattern=None, nextPageURL=None):
        self.name = name
        self.subPattern = subPattern
        self.subURL = subURL
        self.nextPagePattern = nextPagePattern
        self.nextPageURL = nextPageURL
    
    def __str__(self):
        return str((self.name, self.subPattern, self.subURL, self.nextPagePattern, self.nextPageURL))
    
class DataPattern:
    name = None
    dataPattern = None
    dataName = None
    dataURL = None
    
    def __init__(self, name, dataPattern, dataName, dataURL):
        self.name = name
        self.dataPattern = dataPattern
        self.dataName = dataName
        self.dataURL = dataURL
    
    def __str__(self):
        return str((self.name, self.dataPattern, self.dataName, self.dataURL))
        
def getNodeValue(node):
    if not node:
        return None
        
    if len(node.childNodes)==1:
        return node.firstChild.nodeValue
    
    return None
    
def getListPattern(node):
    if not node:
        return None
    
    name = node.getAttribute('name')
    subPattern = None
    subURL = None
    nextPagePattern = None
    nextPageURL = None
    
    for sub_node in node.childNodes:
        if sub_node.nodeName=='subPattern':
            subPattern = getNodeValue(sub_node)
        elif sub_node.nodeName=='subURL':
            subURL = getNodeValue(sub_node)
        elif sub_node.nodeName=='nextPagePattern':
            nextPagePattern = getNodeValue(sub_node)
        elif sub_node.nodeName=='nextPageURL':
            nextPageURL = getNodeValue(sub_node)
    
    return ListPattern(name, subPattern, subURL, nextPagePattern, nextPageURL)

def getDataPattern(node):
    if not node:
        return None
    
    name = node.getAttribute('name')
    dataPattern = None
    dataName = None
    dataURL = None
    
    for sub_node in node.childNodes:
        if sub_node.nodeName=='dataPattern':
            dataPattern = getNodeValue(sub_node)
        elif sub_node.nodeName=='dataName':
            dataName = getNodeValue(sub_node)
        elif sub_node.nodeName=='dataURL':
            dataURL = getNodeValue(sub_node)
    
    return DataPattern(name, dataPattern, dataName, dataURL)

def getConfig():
    pattern_dict = {}

    dom = minidom.parse('conf.xml')
    for node in dom.documentElement.childNodes:
        if node.nodeType == 1:
            if node.nodeName=='pattern':
                #print node.nodeName
                for sub_node in node.childNodes:
                    if sub_node.nodeType == 1:
                        if sub_node.nodeName=='list':
                            name = sub_node.getAttribute('name')
                            pattern_dict[name]=getListPattern(sub_node)
                        elif sub_node.nodeName=='data':
                            name = sub_node.getAttribute('name')
                            pattern_dict[name]=getDataPattern(sub_node)
            elif node.nodeName=='crawling':
                #print node.nodeName
                for sub_node in node.childNodes:
                    if sub_node.nodeType == 1:
                        if sub_node.nodeName=='path':
                            print sub_node.getAttribute('name')
    pprint.pprint(pattern_dict)
    for i in pattern_dict.values():
        print i
    return pattern_dict
    
#------------------------------------------------------------------------------
if __name__ == "__main__":
    getConfig()
                        