import json


BASEHOST = '127.0.0.1'
BASEPORT = 27600

def generate_post_command(args):
    path = "post_echoer"
    url = "http://%s:%d/%s" % (BASEHOST, BASEPORT, path)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(json.dumps(args).encode()))
    }
    data = json.dumps(args).encode()
    request = f"POST /{path} HTTP/1.1\r\n"
    request += f"Host: {BASEHOST}:{BASEPORT}\r\n"
    for key, value in headers.items():
        request += f"{key}: {value}\r\n"
    request += "\r\n" + data.decode()
    return request







args = {'a':'aaaaaaaaaaaaa',
                'b':'bbbbbbbbbbbbbbbbbbbbbb',
                'c':'c',
                'd':'012345\r67890\n2321321\n\r'}
print(generate_post_command(args))