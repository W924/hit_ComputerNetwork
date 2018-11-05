import os
import socket
import gbn
import time


receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiverSocket.bind(('127.0.0.1', 8888))
receiver = gbn.GBNReceiver(receiverSocket)

# fp = open(os.path.dirname(__file__) + '/server/receive_gbn.txt', 'ab')
now_time = time.strftime('%m.%d_%H %M', time.localtime(time.time()))
fp = open(os.path.dirname(__file__) + '/server/' + now_time + '.jpg', 'ab')
reset = False
while True:
    data, reset = receiver.wait_data()
    fp.write(data)
    if reset:
        receiver.expectseqnum = 0
        break

fp.close()
