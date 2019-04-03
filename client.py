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

user_name = input("Enter User Name : ")
pass_name = input("Enter the Password : ")

while True:
    filename = "%d.data" % (int(random.random()*9)+1)
    METHOD = random.choice(["POST","GET"])
    os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s?%s!%s" % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename,user_name,pass_name))
    print (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename)
    time.sleep(10)
