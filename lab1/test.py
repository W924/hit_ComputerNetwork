from hashlib import md5 as m

m1 = m()
m1.update('hello')
m1.update(' ')
m1.update('python')

m2 = m('hello python')

print m1.hexdigest() == m2.hexdigest()
print m1