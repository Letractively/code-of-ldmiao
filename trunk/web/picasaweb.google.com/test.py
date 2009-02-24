import urllib

string = "%E4%B8%80%E5%BC%A0%E5%8F%AA%E8%A6%81%E4%BD%A0%E8%83%BD%E5%9C%A8%E5%9B%BE%E4%B8%AD%E6%89%BE%E5%87%BA9%E9%A2%97%E5%BF%83%E5%B0%B1%E5%8F%AF%E4%BB%A5%E8%AE%B8%E4%B8%AA%E6%84%BF%E6%9C%9B%E8%80%8C%E4%B8%94%E5%AE%83%E4%BC%9A%E9%A9%AC%E4%B8%8A%E5%AE%9E%E7%8E%B0%E7%9A%84%E7%A5%9E%E5%A5%87%E5%9B%BE%E7%89%87.jpg"
print string
print unicode(urllib.unquote_plus(string),"utf8").encode("cp936")