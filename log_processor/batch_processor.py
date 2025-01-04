class BatchProcessor:
    def __init__(self, batch_size):
        self.batch_size = batch_size
        self.logs_batch = []
        self.total_logs = 0
        self.filtered_logs = 0
        self.errors = 0

    def add_log(self, log_entry):
        print(f"Adding log: {log_entry}")
        self.total_logs += 1
        self.logs_batch.append(log_entry)
        print(f"Current batch size: {len(self.logs_batch)}")
        if len(self.logs_batch) >= self.batch_size:
            print("Batch size reached. Processing batch.")
            self.process_batch()
            self.logs_batch = []

    def process_batch(self):
        print(f"Processing batch of {len(self.logs_batch)} logs:")
        for log in self.logs_batch:
            # Print the relevant data (timestamp and message)
            timestamp = log.get("timestamp")
            message = log.get("message")
            print()
            print(f"[{timestamp}] {message}")

        self.filtered_logs += len(self.logs_batch)
        self.logs_batch = []  # Clear the batch after processing

    def flush(self):
        if self.logs_batch:
            self.process_batch()
