#!/usr/bin/python

##########################
# PROXY SERVER
# Last Modified: 13th April, 2017
##########################

import os
import re
import socket
import sys
import threading
import time
# import requests
# import httplib

cache = {}

def bl_parse(a):
    cidr_flag = a.find("/")

    if cidr_flag == -1:
        dom = a
        cidr_flag = False
    else:
        dom = a[:cidr_flag]
        sig = int(a[(cidr_flag + 1):])
    
    dom = dom.split(".")
    for i in range(len(dom)):
        dom[i] = format(int(dom[i]), 'b') # convert segment to binary string

        temp = ""
        if len(dom[i]) < 8:
            for j in range(8 - len(dom[i])):
                temp += "0"
        dom[i] = temp + dom[i] # convert to 8 bit binary string
    dom = "".join(dom)

    if cidr_flag:
        return dom[:sig] # cutoff at sig if cidr
    return dom

def bl_check(host):
    bl_file = "blacklist.txt"

    # b_list = ['127.0.0.1/24']
    try:
        with open(bl_file, 'r') as f:
            b_list = f.readlines() # read file into list
    except IOError:
        print "??? %s not found; unable to check for blacklisting" % (bl_file,)
        return False # return not blacklisted

    ip = socket.gethostbyname(host) # get ip of client requested url
    ip = bl_parse(ip)

    for cidr in b_list:
        flag = True
        c = bl_parse(cidr)

        for i in range(len(c)):
            if c[i] != ip[i]:
               flag = False
               break 

        if flag:
            return flag
    
    return flag

def cache_check(url, conn, client_req):
    print "??? Checking if requested page has been cached"
    TIMEOUT = 5 * 60
    global cache
    t = "time"
    c = "calls"

    orig_url = url
    url_file = ""
    for i in range(len(url)):
        if url[i] != "/":
            url_file += url[i]

    if url not in cache or time.time() - cache[orig_url][t] >= TIMEOUT:
        entry = {t: time.time(), c: 1}
        cache[orig_url] = entry
        return False
    
    cache[orig_url][c] += 1
        
    if cache[orig_url][c] < 4:
        return False

    req = client_req.split("\r\n")

    host = req[1].split(":")[1][1:]
    if len(req[1].split(":")) < 3:
        port = 80
    else:
        port = int(req[1].split(":")[2])

    print "??? Opening socket to end server at", host+":"+str(port)
    sock = socket.socket()
    sock.connect((host, port))

    print "??? Forwarding request on behalf of client to origin server at", url
    
    if host == "localhost" or host == "127.0.0.1":
        print "??? Origin server is located locally"

        method = req[0].split(" ")[0]
        
        http_pos = url.find("://")
        if http_pos != -1:
            url = url[(http_pos + 3):]
        
        file_pos = url.find("/")
        url = url[file_pos:]

        http_ver = req[0].split(" ")[2]

        req[0] = "%s %s %s" % (method, url, http_ver)

        if cache[orig_url][c] > 4:
            req.insert(2, "If-Modified-Since: %s" % (time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(cache[orig_url][c]))))

        new_req = ""
        for l in req:
            new_req += (l + "\r\n")

        print new_req
        sock.send(new_req)

    else:
        print "??? Origin server is located externally"

        req = client_req.split("\r\n")
        if cache[orig_url][c] > 4:
            req.insert(2, "If-Modified-Since: %s" % (time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(cache[orig_url][c]))))

        client_req = ""
        for l in req:
            client_req += (l + "\r\n")

        print client_req
        sock.send(client_req)
        
    print "??? Recieving response from origin server"
    response = sock.recv(1024)
    change = False
    if "304" in response.split("\r\n"):
        change = True
    print response

    print "??? Forwarding response to client"
    temp = response.split("\r\n")
    if not change:
        conn.send(response)
    else:
        temp2 = temp[0].split(" ")
        temp2[1] = "200"
        temp2[2] = "OK"
        temp2 = " ".join(temp2)
        temp[0] = temp2
        response = "\r\n".join(temp)
        conn.send(response)

    if cache[orig_url][c] > 4:
        print "??? Checking if file has been modified at origin server and sending cached file if not modified"
        if change == True:
            cache[orig_url][c] = 4
        else:
            print "??? File has not been modified; sending from cache"
            with open(url_file, 'r') as f:
                while True:
                    data = f.read(1024)
                    conn.send(data)
                    if not data:
                        break
    if cache[orig_url][c] == 4:
        print "??? Recieving fresh data from origin server and forwarding to client"
        cache[orig_url][t] == time.time()
        with open(url_file, 'wb') as f:
            while True:
                data = sock.recv(1024)
                f.write(data)
                conn.send(data)
                if not data:
                    break

    print "??? Client request fulfilled"
    return True

    
def request_handler(conn, addr):
    client_req = conn.recv(1024)
    # print client_req

    req = client_req.split("\r\n")
    url = req[0].split(" ")[1]

    host = req[1].split(":")[1][1:]
    if len(req[1].split(":")) < 3:
        port = 80
    else:
        port = int(req[1].split(":")[2])

    if bl_check(host): # checking if domain is blacklisted
        conn.send("HTTP/1.1 403.6 Forbidden\r\nServer: proxy_server Python/2.7\r\n\r\n")
        conn.send("<html>403 Forbidden\nIP has been blacklisted by proxy server\n</html>")
        print "??? Domain referred to is blacklisted and will not be accessed"
        print "??? Closing connection to client"
        conn.close()
        print "??? Exiting thread"
        print "??? --------------------------------------------------\n\n"
        exit()

    if cache_check(url, conn, client_req):
        print "??? Closing connection to client"
        conn.close()
        print "??? Exiting thread"
        print "??? --------------------------------------------------\n\n"
        exit()
    print "??? Page hasn't been cached yet"

    # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    # r = requests.post(url)
    # print r

    print "??? Opening socket to end server at", host+":"+str(port)
    sock = socket.socket()
    sock.connect((host, port))

    print "??? Forwarding request on behalf of client to origin server at", url
    
    if host == "localhost" or host == "127.0.0.1":
        print "??? Origin server is located locally"

        method = req[0].split(" ")[0]
        
        http_pos = url.find("://")
        if http_pos != -1:
            url = url[(http_pos + 3):]
        
        file_pos = url.find("/")
        url = url[file_pos:]

        http_ver = req[0].split(" ")[2]

        req[0] = "%s %s %s" % (method, url, http_ver)

        new_req = ""
        for l in req:
            new_req += (l + "\r\n")

#         new_req = """GET /2.data HTTP/1.1
# Host: localhost:20101
# User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate
# Connection: keep-alive
# Upgrade-Insecure-Requests: 1


# """

        print new_req
        sock.send(new_req)

    else:
        print "??? Origin server is located externally"

        print client_req
        sock.send(client_req)
        
    print "??? Recieving response from origin server"
    response = sock.recv(1024)
    print response

    print "??? Forwarding response to client"
    conn.send(response)

    print "??? Recieving data from origin server and forwarding to client"
    while True:
        data = sock.recv(1024)
        conn.send(data)
        if not data:
            break
    print "??? Client request fulfilled"

    # conn.send("<html>\n\nSending this from the proxy server to" + str(addr) + "!!!\n\n</html>\r\n")
    print "??? Closing connection to client"
    conn.close()

    print "??? Exiting thread"
    print "??? --------------------------------------------------\n\n"
    exit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: proxy.py <PORT_NUMBER>"
        exit()
    
    port = int(sys.argv[1])
    
    host = ""
    sock = socket.socket()
    sock.bind((host, port))
    print ">>> Proxy server started; listening on port %s" % (port, )
    sock.listen(5)

    while (1):
        conn, addr = sock.accept()
        print ">>> Connection accepted", addr

        global must_quit
        must_quit = threading.Event()
        threading.Timer(0, request_handler, [conn, addr]).start()

        print ">>> thread_initialised"
