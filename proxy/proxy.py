import os
import re
import socket
import sys
import threading

if __name__ == "__main__":
	port = 20100
	host = ""
	instance_socket = socket.socket()
	instance_socket.bind((host, port))
	print (" --> The Proxy Server started; Listening on port %s"%(port,))
	instance_socket.listen(5)

	while(1):
		connection, adderess = instance_socket.accept()
		print ("connection Aceepted",adderess)

		global must_quit
		must_quit = threading.Event()
		threading.Timer(0, request_handler, [connection, addr]).start()

		print (" --> Thread Initialized")