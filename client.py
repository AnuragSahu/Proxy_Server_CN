#! /usr/bin/python

import os
import sys
import random
import time

CLIENT_PORT = int(input("Enter CLIENT_PORT : "))
PROXY_PORT = 20100
SERVER_PORT = int(input("Enter SERVER_PORT : "))

while True:
    filename = "%d.data" % (int(random.random()*9)+1)
    METHOD = random.choice(["POST","GET"])
    print("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s" % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename))
    os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s" % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename))
    print (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename)
    time.sleep(10)
