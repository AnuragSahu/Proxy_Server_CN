#! /usr/bin/python

import os
import sys
import random
import time

if len(sys.argv) < 4:
    print "Usage: python client.py <CLIENT_PORT> <PROXY_PORT> <SERVER_PORT>"
    print "Example: python client.py 20000 20100 20200"
    raise SystemExit

CLIENT_PORT = sys.argv[1]
PROXY_PORT = sys.argv[2]
SERVER_PORT = sys.argv[3]

D = {0: "GET", 1:"POST"}

while True:
    filename = "%d.data" % (int(random.random()*9)+1)
    METHOD = D[int(random.random()*len(D))]
    os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s" % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename))
    # os.system("curl --request %s --local-port %s 127.0.0.1:%s/%s" % (METHOD, CLIENT_PORT, SERVER_PORT, filename))
    # os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s http://gaia.cs.umass.edu/wireshark-labs/HTTP-wireshark-file1.html" % (METHOD, PROXY_PORT, CLIENT_PORT))
    print METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename
    time.sleep(10)
