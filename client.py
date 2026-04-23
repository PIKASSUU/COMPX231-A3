import socket
import sys

class TupleClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def _send(self, cmd_char, key, val=""):
        # Length check: key + value + space ≤ 970
        if len(key)+len(val)+2 > 970:
            return "ERR size exceeds limit"
        msg = f"{cmd_char} {key} {val}".strip()
        pkt = f"{len(msg):03d}{msg}"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.send(pkt.encode())
            resp = s.recv(1024).decode().strip()
        return resp[3:] if len(resp)>=3 else resp