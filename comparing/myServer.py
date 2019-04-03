#!/usr/bin/python

import sys
import os
import time
import SocketServer
import SimpleHTTPServer

msg = "If-Modified-Since"
control_message = 'Cache-control'
cont_msg = 'must-revalidate'
ok_reponse = 200
not_ok_response = 304

class HTTPCacheRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        self.send_response(ok_reponse)
        self.send_header(control_msg, 'no-cache')
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

    def end_headers(self):
        self.send_header(control_msg, cont_msg)
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)
    
    def send_head(self):
        if self.command != "POST" and self.headers.get(msg, None):
            if os.path.isfile(self.path.strip("/")):
                strt = time.strptime(time.ctime(os.path.getmtime(self.path.strip("/"))), "%a %b %d %H:%M:%S %Y")
                ed = time.strptime(self.headers.get(msg, None), "%a %b  %d %H:%M:%S %Z %Y")
                if strt < ed:
                    self.send_response(not_ok_response)
                    self.end_headers()
                    return None
        return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

    
    

if len(sys.argv) < 2:
    print "Needs one argument: server port"
    raise SystemExit

PORT = int(sys.argv[1])

ser = SocketServer.ThreadingTCPServer(("", PORT), HTTPCacheRequestHandler)#.allow_reuse_address = True
ser.allow_reuse_address = True
print "Serving on port", PORT
ser.serve_forever()
