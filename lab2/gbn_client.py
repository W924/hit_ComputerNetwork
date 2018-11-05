import os
import socket
import gbn

senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender = gbn.GBNSender(senderSocket, '127.0.0.1', 8888)

data = []
# fp = open(os.path.dirname(__file__) + '/client/gbn.txt', 'rb')
fp = open(os.path.dirname(__file__) + '/client/data.jpg', 'rb')
while True:
    tmp = fp.read(2048)
    if len(tmp) <= 0:
        break
    data.append(tmp)
print('数据分组个数： ', len(data))

sender.rdt_sent(data)
fp.close()
