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
