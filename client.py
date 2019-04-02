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
	