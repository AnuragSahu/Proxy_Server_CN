
import os
import re
import socket
import sys
import threading
import time
import base64
# import requests
# import httplib

admin_user_name = "abc"
admin_password = base64.standard_b64encode(bytes("def",'utf-8'))
cache = {}; cache_cnt = 0

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
        print("%s not found; unable to check for blacklisting" % (bl_file,))
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
    print("Checking if requested page has been cached")
    TIMEOUT = 5 * 60
    global cache, cache_cnt
    t = "time"
    c = "calls"

    orig_url = url
    url_file = ""
    for i in range(len(url)):
        if url[i] != "/":
            url_file += url[i]

    print("dict = ", orig_url, "path = ", url_file)
    if url not in cache or time.time() - cache[orig_url][t] >= TIMEOUT and cache_cnt < 4:
        entry = {t: time.time(), c: 1}
        cache[orig_url] = entry
        return False
    
    cache[orig_url][c] += 1
        
    if cache[orig_url][c] < 4:
        return False

    req = client_req.decode("ascii").split("\r\n")

    host = req[1].split(":")[1][1:]
    if len(req[1].split(":")) < 3:
        port = 80
    else:
        port = int(req[1].split(":")[2])

    print("Opening socket to end server at", host+":"+str(port))
    sock = socket.socket()
    sock.connect((host, port))

    print("Forwarding request on behalf of client to origin server at", url)
    
    if host == "localhost" or host == "127.0.0.1":
        print("Origin server is located locally")

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

        print(new_req)
        sock.send(new_req.encode())

    else:
        print("Origin server is located externally")

        req = client_req.decode("ascii").split("\r\n")
        if cache[orig_url][c] > 4:
            req.insert(2, "If-Modified-Since: %s" % (time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(cache[orig_url][c]))))

        client_req = ""
        for l in req:
            client_req += (l + "\r\n")

        print(client_req)
        sock.send(client_req.encode())
        
    print("Recieving response from origin server")
    response = sock.recv(1024)
    change = False
    if "304" in response.decode("ascii").split("\r\n"):
        change = True
    print(response)

    print("Forwarding response to client")
    temp = response.decode("ascii").split("\r\n")
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
        print("Checking if file has been modified at origin server and sending cached file if not modified")
        if change == True:
            cache[orig_url][c] = 4
        else:
            print("File has not been modified; sending from cache")
            try:
                f = open(url_file, 'r')
                while True:
                    try:
                        data = f.read(1024)
                        conn.send(data.encode())
                    except:
                        print("File not in text format")
                        break
            except:
                print("File moved from cache. Redirecting to main server")
                break

    if cache[orig_url][c] == 4:
        print("Recieving fresh data from origin server and forwarding to client")
        cache[orig_url][t] == time.time()
        cache_cnt += 1
        with open(url_file, 'wb') as f:
            while True:
                data = sock.recv(1024)
                f.write(data)
                try:
                    conn.send(data)
                except:
                    print("Waiting for client to respond")
                    break
                if not data:
                    break

    print("Client request fulfilled")
    while cache_cnt > 3:
        print('Cache is full. Deleting first record')
        index = list(cache.keys())[0]
        del cache[index]
        index = index.split('/')
        index = index[0]+index[1]
        os.remove(index)
        cache_cnt -= 1

    return True

    
def request_handler(conn, addr):
    client_req = conn.recv(1024)
    req = client_req.decode("ascii").split("\r\n")
    url_large = req[0].split(" ")[1]

    host = req[1].split(":")[1][1:]
    if len(req[1].split(":")) < 3:
        port = 80
    else:
        port = int(req[1].split(":")[2])

    if port < 20000 or port > 20200:
        print("Invalid port address", port)
        exit()
    http_pos = url_large.find("://")
    if http_pos != -1:
        url_large = url_large[(http_pos + 3):]

    file_pos = url_large.find("/")
    file_pos_end = url_large.find("?")
    url = url_large[file_pos:file_pos_end]
    nme_pos = url_large.find("!")
    user_name = url_large[file_pos_end+1:nme_pos]
    pass_name = base64.standard_b64encode(bytes(url_large[nme_pos+1 : ],'utf-8'))

    if(user_name==admin_user_name and pass_name==admin_password):
        print("----> User Authenticated to use black Listed Hosts")

    elif bl_check(host): # checking if domain is blacklisted
        print("----> User Not Authenticated to use blacklisted Hosts")
        conn.send("HTTP/1.1 403.6 Forbidden\r\nServer: proxy_server Python/2.7\r\n\r\n")
        conn.send("<html>403 Forbidden\nIP has been blacklisted by proxy server\n</html>")
        print("Domain referred to is blacklisted and will not be accessed")
        print ("Closing connection to client")
        conn.close()
        print ("Exiting thread")
        print ("--------------------------------------------------\n")
        exit()
    else : print(" ----> User Not Authenticated to use blacklisted Hosts")

    if cache_check(url, conn, client_req):
        print ("Closing connection to client")
        conn.close()
        print ("Exiting thread")
        print ("--------------------------------------------------\n")
        exit()
    print("Page hasn't been cached yet")

    
    print("Opening socket to end server at", host+":"+str(port))
    sock = socket.socket()
    sock.connect((host, port))

    print ("Forwarding request on behalf of client to origin server at", url_large)
    
    if host == "localhost" or host == "127.0.0.1":
        print("Origin server is located locally")

        method = req[0].split(" ")[0]
        
        http_pos = url_large.find("://")
        if http_pos != -1:
            url_large = url_large[(http_pos + 3):]
        
        

        http_ver = req[0].split(" ")[2]

        req[0] = "%s %s %s" % (method, url, http_ver)

        new_req = ""
        for l in req:
            new_req += (l + "\r\n")


        print(new_req)
        sock.send(new_req.encode())

    else:
        print("Origin server is located externally")

        print(client_req)
        sock.send(client_req.encode())
        
    print("Recieving response from origin server")
    response = sock.recv(1024)
    print(response)

    print("Forwarding response to client")
    conn.send(response)

    print("Recieving data from origin server and forwarding to client")
    while True:
        data = sock.recv(1024)
        try:
            conn.send(data)
        except:
            print("Waiting for server to respond")
            break
        if not data:
            break
    print("Client request fulfilled")

    print("Closing connection to client")
    conn.close()

    print("Exiting thread")
    print("--------------------------------------------------\n")
    exit()


def main():
    port = 20100
    
    host = ""
    sock = socket.socket()
    sock.bind((host, port))
    print("Proxy server started; listening on port %s" % (port, ))
    sock.listen(5)

    while (1):
        conn, addr = sock.accept()
        if addr[1] >= 20000 and addr[1] < 20100:
            print("Client from inside network", addr[1])

            global must_quit
            must_quit = threading.Event()
            threading.Timer(0, request_handler, [conn, addr]).start()

            print("Thread_initialised")
        else:
            print("Connnection from outside network - ", addr[1],". Not accepted")

if __name__ == "__main__":
    main()    
