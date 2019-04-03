#! /usr/bin/python

import os
import sys
import random
import time

CLIENT_PORT = int(input("Enter CLIENT_PORT : "))
PROXY_PORT = 20100
SERVER_PORT = int(input("Enter SERVER_PORT : "))
if(CLIENT_PORT > 20200 or CLIENT_PORT < 20000):
    print ("Please Enter Client port Between 20000 and 20099")
    CLIENT_PORT = int(input(""));

if(SERVER_PORT > 20200 or SERVER_PORT < 20000):
    print ("Please Enter Server port Between 20000 and 20200")
    SERVER_PORT = int(input(""));

while True:
    filename = "%d.data" % (int(random.random()*9)+1)
    METHOD = random.choice(["POST","GET"])
    os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s" % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename))
    # os.system("curl --request %s --local-port %s 127.0.0.1:%s/%s" % (METHOD, CLIENT_PORT, SERVER_PORT, filename))
    # os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file1.html" % (METHOD, PROXY_PORT, CLIENT_PORT))
    print (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename)
    time.sleep(10)
