# coding:utf-8
import random
import socket
import struct
import time

LOSS_RATE = 0.1


# GBN发送端
class GBNSender:
    def __init__(self, sender_socket, host, port):
        self.sender_socket = sender_socket      # 发送端套接字
        self.address = (host, port)             # 目的地址
        self.window_size = 4                    # 窗口大小
        self.timeout = 8                       # 超时时间
        self.loss_rate = LOSS_RATE              # 丢包率
        self.base = 0                           # 窗口头部序列号
        self.nextseqnum = 0                     # 下一个可用的序列号
        self.buffer = [None] * 256              # 数据分组

    # 从上层接收数据并发送给接收方
    def rdt_sent(self, data):
        # print(data)
        count = 0
        while True:
            while self.nextseqnum < (self.base + self.window_size):
                if count >= len(data):
                    break
                # 发送窗口未被占满
                data_send = data[count]
                checksum = self.get_checksum(data_send)
                if count < len(data) - 1:
                    # 不是最后一个数据分组，则标志位为0
                    self.buffer[self.nextseqnum] = struct.pack('BBB', self.nextseqnum, 0, checksum) + data_send
                else:
                    # 如果是最后一个数据分组，则标志位为1
                    self.buffer[self.nextseqnum] = struct.pack('BBB', self.nextseqnum, 1, checksum) + data_send
                print('发送端发送数据分组：', count)
                # 使用udp传输数据
                self.udp_send(self.buffer[self.nextseqnum])
                # 序列号取值范围设为 0~255
                self.nextseqnum = (self.nextseqnum + 1) % 256
                count += 1
            self.wait_ack()
            if count >= len(data):
                break

    # 收到确认分组后进行的操作
    def wait_ack(self):
        self.sender_socket.settimeout(self.timeout)
        count = 0
        while True:
            try:
                data_rcv, address = self.sender_socket.recvfrom(4096)
                ack_seq = data_rcv[0]       # 接收方最近一次确认的数据分组的序列号
                expect_seq = data_rcv[1]    # 接收方期望收到的数据分组的序列号
                print('发送端接收ACK:', "ack", ack_seq, "expect", expect_seq)
                self.base = max(self.base, (ack_seq + 1) % 256)
                # 已发送分组确认完毕，则停止定时器
                if self.base == self.nextseqnum:
                    self.sender_socket.settimeout(None)
                    break
            # 如果发生超时现象，重发所有未确认的分组
            except socket.timeout:
                count += 1
                print('发送端等待ack超时')
                # 重发未确认的分组
                for i in range(self.base, self.nextseqnum):
                    print('发送端重新发送数据分组：', i)
                    self.udp_send(self.buffer[i])
                # 重新启动定时器
                self.sender_socket.settimeout(self.timeout)
            # 如果多次超时，则终止
            if count >= 8:
                break

    # 计算校验和
    def get_checksum(self, data):
        length = len(str(data))
        checksum = 0
        for i in range(0, length):
            checksum += int.from_bytes(bytes(str(data)[i], encoding='utf-8'), byteorder='little')
            checksum &= 0xFF
        return checksum

    # 使用udp发送分组
    def udp_send(self, data):
        if random.random() >= self.loss_rate:
            self.sender_socket.sendto(data, self.address)
        else:
            print('分组丢失')
        time.sleep(0.3)


# GBN接收方
class GBNReceiver:
    def __init__(self, receiver_socket):
        self.receiver_socket = receiver_socket      # 接收端套接字
        self.loss_rate = LOSS_RATE                          # 丢包率
        self.expectseqnum = 0                       # 初始化期望收到的分组序列号
        self.timeout = 8                           # 超时时间
        self.target = None                          # 发送端地址

    # 收到数据分组后进行的操作
    def wait_data(self):
        while True:
            data, address = self.receiver_socket.recvfrom(4096)
            self.target = address
            ack = data[0]
            flag = data[1]
            checksum = data[2]
            data_deliver = data[3:]
            print('接收端接收分组：', ack)
            # 如果收到期望数据包且未出错时，才会将数据交给接收方
            if ack == self.expectseqnum and self.get_checksum(data_deliver) == checksum:
                self.expectseqnum = (self.expectseqnum + 1) % 256
                ack_pkt = struct.pack('BB', ack, self.expectseqnum)
                self.udp_send(ack_pkt)
                # 如果是最后一个数据分组，通告上层
                if flag:
                    return data_deliver, True
                else:
                    return data_deliver, False
            # 如果有错的话，则再发送最近按序接收的分组的ACK
            else:
                ack_pkt = struct.pack('BB', (self.expectseqnum - 1) % 256, self.expectseqnum)
                self.udp_send(ack_pkt)

    # 计算校验和
    def get_checksum(self, data):
        length = len(str(data))
        checksum = 0
        for i in range(0, length):
            checksum += int.from_bytes(bytes(str(data)[i], encoding='utf-8'), byteorder='little')
            checksum &= 0xFF
        return checksum

    # 使用udp发送确认分组
    def udp_send(self, pkt):
        # 通过LOSS_RATA来模拟确认报文丢失，引起超时现象
        if random.random() >= self.loss_rate:
            self.receiver_socket.sendto(pkt, self.target)
            print('接收端发送: ack ', pkt[0], 'expect ', pkt[1])
        else:
            print('接收端发送: ack ', pkt[0], 'expect ', pkt[1], ', 但已丢失')
            time.sleep(0.3)
