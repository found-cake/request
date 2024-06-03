import socket
import time
from json.encoder import JSONEncoder

METHOD_GET = 'GET'
METHOD_POST = 'POST'
METHOD_PUT = 'PUT'
METHOD_DELETE = 'DELETE'

def send_request(method: str, url: str, headers: dict = None, data: str or dict = None, cookies: dict = None, timeout: float = 30, print_time: bool = True):
    url_parts = url.split('/')
    host = url_parts[2]
    path = '/' + '/'.join(url_parts[3:])
    
    request = f"{method} {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    
    if headers is not None:
        for header, value in headers.items():
            request += f"{header}: {value}\r\n"
    
    if cookies is not None:
        cookie_str = "; ".join([f"{key}={value}" for key, value in cookies.items()])
        request += f"Cookie: {cookie_str}\r\n"
    
    if data is not None:
        if type(data) == dict:
            data = JSONEncoder().encode(data)
        request += f"Content-Length: {len(data)}\r\n\r\n{data}"
    else:
        request += "\r\n"
    
    response = b''
    is_first = True
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            r = host.split(":")
            target = (r[0], int(r[1]))
        except (IndexError, ValueError):
            target = (host, 80)
        start = time.time_ns()
        s.settimeout(timeout)
        s.connect(target)
        s.sendall(request.encode())
    
        while True:
            try:
                chunk = s.recv(4096)
                if len(chunk) == 0:
                    break
                response += chunk
                if is_first:
                    s.settimeout(0.0001)
                    is_first = False
            except socket.timeout:
                break
    
    if print_time:
        print("걸린시간: ", (time.time_ns() - start) / 10**9, "s")
    
    return response.decode()
