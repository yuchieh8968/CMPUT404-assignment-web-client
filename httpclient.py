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

# Copyright 2023 Jeff Wang
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
import sys
import socket
import urllib.parse

BYTES_TO_READ = 4096


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

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
        # https: // www.w3.org / International / articles / http - charset / index
        # call parse function to handle input url and separate info into a list
        # parsed = protocol, host, port, full path
        parsed = self.parse(url)

        # build request with parsed input
        # https://docs.python.org/3/library/string.html
        request = "GET {} HTTP/1.1\r\nHOST: {}\r\n\r\n".format(parsed[3], parsed[1])

        # code excerpt from lab2 proxy_client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((parsed[1], int(parsed[2])))
            s.send(request.encode())
            s.shutdown(socket.SHUT_WR)

            chunk = s.recv(BYTES_TO_READ)
            result = b'' + chunk

            while len(chunk) > 0:
                chunk = s.recv(BYTES_TO_READ)
                result += chunk

        # separate header and body content by the first b'\r\n\r\n'
        header, body = result.split(b'\r\n\r\n', 1)

        # convert to string and return
        body = str(body)

        # retrieve code from header and return
        code = int(header.split(b' ')[1])

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # call parse function to handle input url and separate info into a list
        # parsed = protocol, host, port, full path

        parsed = self.parse(url)
        # if no arguments are passed through, don't add arguments to the request
        try:
            # https://docs.python.org/3/library/urllib.parse.html
            argument = urllib.parse.urlencode(args).encode('utf-8')
            # https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#/32
            # create request function with Accept Encoding, Content Type and Content Length in header, if arguments is passed append to the end
            request = "POST {} HTTP/1.1\r\nHost: {}:{}\r\nAccept-Encoding: gzip, deflate\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}".format(
                parsed[3], parsed[1], parsed[2], len(argument) + 2, argument).encode("utf-8")
        except TypeError:
            # create request function with Accept Encoding, Content Type and Content Length in header, without arguments
            request = "POST {} HTTP/1.1\r\nHost: {}:{}\r\nAccept-Encoding: gzip, deflate\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n".format(
                parsed[3], parsed[1], parsed[2], 0).encode("utf-8")

        # code excerpt from lab2 proxy_client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((parsed[1], int(parsed[2])))
            s.send(request)
            s.shutdown(socket.SHUT_WR)
            chunk = s.recv(BYTES_TO_READ)
            result = b'' + chunk
            while len(chunk) > 0:
                chunk = s.recv(BYTES_TO_READ)
                result += chunk
            s.close()

        # separate header from content
        header, content = result.split(b'\r\n', 1)

        # separate body from result
        body = content.split(b"\r\n\r\n", 1)[1]

        # replace the extra character from encoding and decoding
        temp = body.decode()
        body = temp.replace("b'", "")

        # extract response code from header
        code = header.split(b' ')[1]
        code = int(code)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

    # https://docs.python.org/3/library/urllib.parse.html
    def parse(self, url):
        parsed_elements = []

        # extract information from input url. If host and port is provided append it to list, if not, only protocol and fullPath is appended
        try:
            protocol, path1 = url.split("://", 1)
            host, path2 = path1.split(":", 1)
            port, fullPath = path2.split("/", 1)
            fullPath = "/" + fullPath

            parsed_elements.append(protocol)
            parsed_elements.append(host)
            parsed_elements.append(port)
            parsed_elements.append(fullPath)

        except ValueError:
            # "http://www.cs.ualberta.ca/"
            protocol, fullPath = url.split("://", 1)
            fullPath = "/" + fullPath

            parsed_elements.append(protocol)
            parsed_elements.append(fullPath)

        return parsed_elements


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
