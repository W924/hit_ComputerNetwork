import urlparse

# url = "https://www.google.com.hk:8080/home/search;12432?newwi.1.9.serpuc#1234"
url = "www.baidu.com/"
r = urlparse.urlparse(url)
print r
print r.port
print r.hostname
print r.geturl()