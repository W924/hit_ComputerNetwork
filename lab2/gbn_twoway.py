import socket
import threading
import os
import time
import gbn


def send(sender, filepath):
    fp = open(filepath + 'data.jpg', 'rb')
    data = []
    while True:
        tmp = fp.read(2048)
        if len(tmp) <= 0:
            break
        data.append(tmp)
    print('数据分组个数: ', len(data))

    sender.rdt_sent(data)
    fp.close()


def receive(receiver, filepath):
    now_time = time.strftime('%m.%d_%H %M', time.localtime(time.time()))
    fp = open(filepath + now_time + '.jpg', 'ab')
    reset = False
    while True:
        data, reset = receiver.wait_data()
        fp.write(data)
        if reset:
            receiver.expect_seq = 0
            break
    fp.close()


# client发送方
client_senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_sender = gbn.GBNSender(client_senderSocket, '127.0.0.1', 8888)

# client接收方
client_receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_receiverSocket.bind(('127.0.0.1', 8080))
client_receiver = gbn.GBNReceiver(client_receiverSocket)
threading.Thread(target=receive, args=(client_receiver, os.path.dirname(__file__) + '/client/')).start()

# server发送方
server_senderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sender = gbn.GBNSender(server_senderSocket, '127.0.0.1', 8080)

# server接收方
server_receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_receiverSocket.bind(('127.0.0.1', 8888))
server_receiver = gbn.GBNReceiver(server_receiverSocket)
threading.Thread(target=receive, args=(server_receiver, os.path.dirname(__file__) + '/server/')).start()

send(client_sender, os.path.dirname(__file__) + '/client/')
send(server_sender, os.path.dirname(__file__) + '/server/')
