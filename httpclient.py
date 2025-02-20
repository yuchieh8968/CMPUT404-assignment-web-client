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
import time

# initialize length of bytes to read
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
        # https://www.w3.org/International/articles/http-charset/index
        # https://docs.python.org/3/library/urllib.parse.html
        parsed = urllib.parse.urlparse(url)

        # build request with parsed input
        # https://docs.python.org/3/library/string.html
        # if an argument exists have it at the end of the request
        if args == None:
            request = "GET {} HTTP/1.1\r\nHOST: {}\r\n\r\n".format(url, parsed.hostname)
        else:
            argument = urllib.parse.urlencode(args).encode('utf-8')
            request = "GET {} HTTP/1.1\r\nHOST: {}\r\n\r\n{}".format(url, parsed.hostname, argument)
        # code excerpt from lab2 proxy_client
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if parsed.port == None:
                    port = 80
                else:
                    port = parsed.port

                s.connect((parsed.hostname, port))
                s.sendall(request.encode())
                time.sleep(3)

                s.shutdown(socket.SHUT_WR)
                chunk = s.recv(BYTES_TO_READ)

                result = b'' + chunk

                while len(chunk) > 0:
                    chunk = s.recv(BYTES_TO_READ)
                    result += chunk
                s.close()

            # separate header and body content by the first b'\r\n\r\n'
            header, body = result.split(b'\r\n\r\n', 1)

            # convert to string and return
            body = str(body)

            # retrieve code from header and return
            code = int(header.split(b' ')[1])

            return HTTPResponse(code, body)

        # if socket receives these errors because of bad url return Invalid path and stop program
        except socket.gaierror or TypeError:
            print("Invalid Path")
            sys.exit(1)

    def POST(self, url, args=None):
        # https://docs.python.org/3/library/urllib.parse.html
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc == None or parsed.netloc == " ":
            sys.stdout("Not proper URL")
            sys.exit(1)

        # if no arguments are passed through, don't add arguments to the request
        if args is None:
            request = "POST {} HTTP/1.1\r\nHost: {}:{}\r\nAccept-Encoding: gzip, deflate\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n".format(
                url, parsed.hostname, parsed.port, 0).encode("utf-8")
        else:
            argument = urllib.parse.urlencode(args).encode('utf-8')
            request = "POST {} HTTP/1.1\r\nHost: {}:{}\r\nAccept-Encoding: gzip, deflate\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\n\r\n{}".format(
                url, parsed.hostname, parsed.port, len(argument) + 2, argument).encode("utf-8")

        try:
            # code excerpt from lab2 proxy_client
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((parsed.hostname, parsed.port))
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
            print(body)

            return HTTPResponse(code, body)

        # if socket receives these errors because of bad url return Invalid path and stop program
        except socket.gaierror or TypeError:
            print("Invalid Path")
            sys.exit(1)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        # update print statement so it returns result to stdout for user to see
        print(client.command(sys.argv[2], sys.argv[1]).body)
    else:
        # update print statement so it returns result to stdout for user to see
        print(client.command(sys.argv[1]).body)
