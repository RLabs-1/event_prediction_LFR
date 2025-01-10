import re
import time
from collections import deque
from datetime import datetime


class LogFilter:
    def __init__(self, include_keywords, exclude_keywords, date_range):
        self.include_keywords = include_keywords
        self.exclude_keywords = exclude_keywords
        self.date_range = date_range
        self.level = "ERROR"

    def is_within_date_range(self, log_date):
        start = datetime.strptime(self.date_range['start'], "%Y-%m-%d")
        end = datetime.strptime(self.date_range['end'], "%Y-%m-%d")
        return start <= log_date <= end

    def filter_log(self, log_entry):
        message = log_entry.get("message", "")
        include_check = any(keyword in message for keyword in self.include_keywords)
        exclude_check = any(keyword in message for keyword in self.exclude_keywords)
        return include_check and not exclude_check

    # ammar
    def filter_by_level(self, log_entry):
        # Exclude specific log levels
        return log_entry["level"] in self.level  ## should get yaml fail


class CircularBuffer:
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size)

    def add_event(self, event):
        self.buffer.append(event)

    def get_all_events(self):
        return list(self.buffer)


# # Example Usage
# buffer = CircularBuffer(max_size=1000)  # Max 1000 events
# buffer.add_event({"log_level": "info", "message": "New event"})


def flush_buffer(buffer, kafka_producer, topic):
    while True:
        if len(buffer) > 0:
            batch = buffer.get_all_events()
            for event in batch:
                kafka_producer.send(topic, event)
            buffer.clear()
        time.sleep(5)  # Flush every 5 seconds
