#! /usr/bin/python

import os
import sys
import random
import time
import base64

CLIENT_PORT = int(input("Enter CLIENT_PORT : "))
PROXY_PORT = 20100
SERVER_PORT = int(input("Enter SERVER_PORT : "))

user_name = raw_input("Enter User Name : ")
pass_name = raw_input("Enter the Password : ")
#pass_name = base64.standard_b64encode(pass_name)

while True:
    filename = "%d.data" % (int(random.random()*9)+1)
    METHOD = random.choice(["POST","GET"])
    os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s?%s!%s" % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename,user_name,pass_name))
    print (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename)
    time.sleep(10)
