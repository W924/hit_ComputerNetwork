import datetime

a = "Wed, 06 Jul 2016 03:06:11 GMT"
b = "Wed, 31 Oct 2018 10:21:19 GMT"
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
a_ = datetime.datetime.strptime(a, GMT_FORMAT)
b_ = datetime.datetime.strptime(b, GMT_FORMAT)
print a_ < b_
