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
    
    def run_file(self, path):
        try:
            with open(path) as f: lines = f.readlines()
        except:
            print(f"File not found: {path}")
            return
        for line in lines:
            line = line.strip()
            if not line: continue
            parts = line.split()
            cmd = parts[0]
            try:
                if cmd == 'READ':
                    k = parts[1]
                    res = self._send('R', k)
                    print(f"READ {k}: {res}")
                elif cmd == 'GET':
                    k = parts[1]
                    res = self._send('G', k)
                    print(f"GET {k}: {res}")
                elif cmd == 'PUT':
                    k = parts[1]
                    v = ' '.join(parts[2:]) if len(parts)>=3 else ''
                    res = self._send('P', k, v)
                    print(f"PUT {k} {v}: {res}")
            except:
                print(f"Invalid line: {line}")

if __name__ == "__main__":
    if len(sys.argv)!=4:
        print("Usage: python client.py <host> <port> <request.txt>")
        sys.exit(1)
    TupleClient(sys.argv[1], int(sys.argv[2])).run_file(sys.argv[3])