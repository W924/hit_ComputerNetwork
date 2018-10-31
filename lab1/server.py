# coding:utf-8
import socket
import urlparse
import threading
import os
import hashlib
import time
import datetime

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

Network_Filtering = [
    # 'www.qq.com',
    'today.hit.edu.cn'
]

User_Filtering = [
    # '127.0.0.1'
]

SITE_GUIDE = {
    'hitgs.hit.edu.cn': 'jwts.hit.edu.cn'
}


def init_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    return s


def proxy(conn, addr):
    max_len = 4096                        # 接受的最大数据量
    source_socket = conn
    request_message = source_socket.recv(max_len)
    # 处理空报文段
    if not request_message:
        source_socket.close()
        return
    # print request_message

    request_line = request_message.split('\n')[0]             # 请求行
    remain_lines = request_message[request_message.find('\n') + 1:]         # 剩余字段，其中包括首部行以及数据主体
    # print remain_lines
    # print request_line

    method = request_line.split()[0]
    path = request_line.split()[1]
    url = urlparse.urlparse(path)
    version = request_line.split()[2]
    # print request_line
    # print path
    # print url
    # print url.hostname

    data = "%s %s %s\r\n" % (method, path, version)
    send_message = data + remain_lines
    # print send_message

    hostname = url.hostname
    if not hostname:
        source_socket.close()
        return
    # print hostname
    port = 80
    if url.port is not None:
        port = url.port
    # print port

    # 实现网络过滤
    if hostname in Network_Filtering:
        source_socket.send('403 Forbidden\r\n')
        source_socket.close()
        return

    # 实现用户过滤
    if addr[0] in User_Filtering:
        source_socket.send('403 Forbidden\r\n')
        source_socket.close()
        return

    # 实现网站引导（钓鱼）
    if hostname in SITE_GUIDE.keys():
        send_message = send_message.replace(url.hostname, SITE_GUIDE[url.hostname])
        hostname = SITE_GUIDE[url.hostname]

    # 向服务器发送请求报文，分是否已经缓存两种情况
    dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest_socket.connect((hostname, port))

    m = hashlib.md5()
    m.update(url.netloc + url.path)

    # 在目录下创建一个文件夹，并将所有的缓存文件存在该目录下
    filepath = os.path.join(os.path.dirname(__file__), 'cache')
    if not os.path.exists(filepath):
        os.mkdir(filepath)

    filename = os.path.join(filepath, m.hexdigest() + '.cached')
    if os.path.exists(filename):
        # 如果有缓存，则需要If-Modified-Since首部字段来确定是否为最新的
        new_message = request_line + '\n'
        t = (time.strptime(time.ctime(os.path.getmtime(filename)), "%a %b %d %H:%M:%S %Y"))
        # print time.strftime('%a, %d %b %Y %H:%M:%S GMT', t)
        new_message += 'If-Modified-Since: ' + time.strftime('%a, %d %b %Y %H:%M:%S GMT', t) + '\n'
        for line in request_message.split('\n')[1:]:
            new_message += line + '\n'
        dest_socket.send(new_message)
        print new_message

        count = 0
        while True:
            data = dest_socket.recv(max_len)
            # print data
            fp = open(filename, 'wb')
            if count == 0:
                loc1 = data.find("Last-Modified")
                # print loc1
                if loc1 >= 0:
                    b = data[loc1:]
                    loc2 = b.find('\r\n')
                    c = b[15:loc2]         # 为GMT格式
                    now_time = datetime.datetime.strptime(time.strftime('%a, %d %b %Y %H:%M:%S GMT', t), GMT_FORMAT)
                    last_time = datetime.datetime.strptime(c, GMT_FORMAT)
                    # print "now time: ", now_time
                    # print "last modified time: ", last_time
                    if now_time > last_time:   # 说明没有被修改过
                        print "--------------this page has not been modified------------------"
                        source_socket.send(open(filename, 'rb').read())
                        break
                    else:                      # 如果被修改过，则将新的报文返回给客户端
                        if len(data) > 0:
                            source_socket.send(data)
                            fp.write(data)
                        else:
                            break
                else:
                    if len(data) > 0:
                        source_socket.send(data)
                        fp.write(data)
                    else:
                        break
            else:
                if len(data) > 0:
                    source_socket.send(data)
                    fp.write(data)
                else:
                    break
            count += 1
    else:
        # 如果没有缓存，则直接请求对象
        print send_message
        dest_socket.send(send_message)
        # 等待响应报文，接收后需缓存
        fp = open(filename, 'ab')
        while True:
            data = dest_socket.recv(max_len)
            # print data
            if len(data) > 0:
                fp.write(data)
                source_socket.send(data)
            else:
                break


def proxy_run(s):
    while True:
        connect, address = s.accept()
        proxy_thread = threading.Thread(target=proxy, args=(connect, address))
        proxy_thread.start()


proxy_socket = init_socket('127.0.0.1', 8080)
proxy_run(proxy_socket)
