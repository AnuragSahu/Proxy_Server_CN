import os
import sys
import random
import time

print ("You will have to enter the Following information:")
print ("Client Port Number : ")
CLIENT_PORT = int(input(""));
print ("Proxy Port Number : ")
PROXY_PORT = int(input(""))
print ("Server Port Number : ")
SERVER_PORT = int(input(""))

request_type = {1: "POST", 0: "GET"}

while True:
	filename = "%d.data" % (int(random.random()*9)+1)
	METHOD = D[int(random.random()*len(D))]
	os.system("curl --request %s --proxy 127.0.0.1:%s --local-port %s 127.0.0.1:%s/%s" % (METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename))
	print METHOD, PROXY_PORT, CLIENT_PORT, SERVER_PORT, filename
	time.sleep(10)