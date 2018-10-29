# coding:utf-8
import socket
import urlparse
import threading

Network_Filtering = [
    # 'www.qq.com',
    'today.hit.edu.cn'
]

User_Filtering = [
    '127.0.0.12'
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
    print request_message

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

    # # 实现用户过滤
    # if addr[0] in User_Filtering:
    #     source_socket.send('403 Forbidden\r\n')
    #     print "You are not allowed to visit external sites"
    #     source_socket.close()
    #     return
    #
    # 实现网站引导（钓鱼）
    if hostname in SITE_GUIDE.keys():
        send_message = send_message.replace(url.hostname, SITE_GUIDE[url.hostname])
        hostname = SITE_GUIDE[url.hostname]
    print request_message

    # 向服务器发送请求报文
    dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest_socket.connect((hostname, port))
    dest_socket.send(send_message)
    # print send_message

    # 等待响应报文
    while True:
        data = dest_socket.recv(max_len)
        if len(data) > 0:
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
