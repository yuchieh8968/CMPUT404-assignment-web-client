#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
BYTES_TO_READ = 4096
def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 200

        # protocol, host, port, fullpath
        # http, 127.0.0.1, 27656, /abcdef/gjkd/dsadas
        parsed = self.parse(url)
        print(parsed)
        request = "GET {} HTTP/1.1\r\nHOST: {}\r\n\r\n".format(parsed[3], parsed[1])
        print(request)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((parsed[1], int(parsed[2])))
            s.send(request.encode())
            s.shutdown(socket.SHUT_WR)

            chunk = s.recv(BYTES_TO_READ)
            result = b'' + chunk

            while len(chunk) > 0:
                chunk = s.recv(BYTES_TO_READ)
                result += chunk

            print("_________________________",result)

        header= result.split(b'\r\n', 1)[0]
        code = header.split(b' ')[1]
        print(header, code)
        code = int(code)


        #status_code = header.split(b"\r\n")[0].decode().split(" ")[1]
        return HTTPResponse(code, request)


    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

    def parse(self, url):
        parsed_elements = []
        protocol, path1 = url.split("://", 1)
        host, path2 = path1.split(":", 1)
        port, fullPath = path2.split("/", 1)
        fullPath = "/"+fullPath

        parsed_elements.append(protocol)
        parsed_elements.append(host)
        parsed_elements.append(port)
        parsed_elements.append(fullPath)

        return parsed_elements
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
