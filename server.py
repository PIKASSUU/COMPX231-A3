import socket
import threading
import time
from typing import Dict

class TupleSpaceServer:
    def __init__(self, port: int):
        self.host = '0.0.0.0'
        self.port = port
        self.tuple_space: Dict[str, str] = {}
        self.lock = threading.Lock()

        # Statistics fields
        self.total_clients = 0
        self.total_operations = 0
        self.total_reads = 0
        self.total_gets = 0
        self.total_puts = 0
        self.total_errors = 0

        # Start the statistics thread
        self.stats_thread = threading.Thread(target=self._print_stats_periodically, daemon=True)
        self.stats_thread.start()

    def _parse_request(self, data: str):
        if len(data) < 3:
            return "", "", ""
        msg_len = int(data[:3])
        body = data[3:].strip()

        if body.startswith('R '):
            return 'READ', body[2:].strip(), ''
        elif body.startswith('G '):
            return 'GET', body[2:].strip(), ''
        elif body.startswith('P '):
            parts = body[2:].split(' ', 1)
            key = parts[0] if parts else ''
            val = parts[1] if len(parts) > 1 else ''
            return 'PUT', key, val
        return "", "", ""
    
    def _process_request(self, cmd: str, key: str, val: str):
        with self.lock:
            self.total_operations += 1
            if cmd == 'READ':
                self.total_reads += 1
                if key in self.tuple_space:
                    res = f"OK ({key}, {self.tuple_space[key]}) read"
                else:
                    self.total_errors += 1
                    res = f"ERR {key} does not exist"
            elif cmd == 'GET':
                self.total_gets += 1
                if key in self.tuple_space:
                    v = self.tuple_space.pop(key)
                    res = f"OK ({key}, {v}) removed"
                else:
                    self.total_errors += 1
                    res = f"ERR {key} does not exist"
            elif cmd == 'PUT':
                self.total_puts += 1
                if key not in self.tuple_space:
                    self.tuple_space[key] = val
                    res = f"OK ({key}, {val}) added"
                else:
                    self.total_errors += 1
                    res = f"ERR {key} already exists"
            else:
                self.total_errors += 1
                res = "ERR invalid command"
            return f"{len(res):03d}{res}"
        
    def _handle_client(self, sock: socket.socket):
        with self.lock:
            self.total_clients += 1
        try:
            while True:
                data = sock.recv(1024).decode().strip()
                if not data: break
                cmd, k, v = self._parse_request(data)
                resp = self._process_request(cmd, k, v)
                sock.send(resp.encode())
        except:
            pass
        finally:
            sock.close()

    def _print_stats_periodically(self):
        while True:
            time.sleep(10)
            with self.lock:
                n = len(self.tuple_space)
                if n == 0:
                    avg_tup = avg_k = avg_v = 0
                else:
                    ks = [len(x) for x in self.tuple_space.keys()]
                    vs = [len(x) for x in self.tuple_space.values()]
                    avg_k = sum(ks)/n
                    avg_v = sum(vs)/n
                    avg_tup = (sum(ks)+sum(vs))/n
                print("\n===== Tuple Space Stats =====")
                print(f"Tuples: {n}")
                print(f"Avg tuple size: {avg_tup:.2f}")
                print(f"Avg key size: {avg_k:.2f}")
                print(f"Avg value size: {avg_v:.2f}")
                print(f"Clients: {self.total_clients}")
                print(f"Ops: {self.total_operations} | READ:{self.total_reads} GET:{self.total_gets} PUT:{self.total_puts}")
                print(f"Errors: {self.total_errors}")
                print("=============================\n")

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(10)
        print(f"Server running on {self.host}:{self.port}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=self._handle_client, args=(conn,)).start()

if __name__ == "__main__":
    import sys
    if len(sys.argv)!=2:
        print("Usage: python server.py <port> (50000-59999)")
        sys.exit(1)
    port = int(sys.argv[1])
    if not 50000<=port<=59999:
        print("Port must be 50000~59999")
        sys.exit(1)
    TupleSpaceServer(port).start()