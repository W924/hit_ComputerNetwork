import os
import socket
import time
import sr


receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiverSocket.bind(('127.0.0.1', 8888))
receiver = sr.SRReceiver(receiverSocket)

now_time = time.strftime('%m.%d_%H %M', time.localtime(time.time()))
fp = open(os.path.dirname(__file__) + '/server/' + now_time + '.jpg', 'ab')
reset = False
while True:
    data, reset = receiver.wait_data()
    fp.write(data)
    if reset:
        break

fp.close()
