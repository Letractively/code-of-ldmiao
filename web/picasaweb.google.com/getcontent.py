import urllib

proxies = {'http': 'http://web-proxy.hpl.hp.com:8088'}

filehandle = urllib.urlopen("http://picasaweb.google.com/jallintang/Year", proxies=proxies)
content = filehandle.read()
print content