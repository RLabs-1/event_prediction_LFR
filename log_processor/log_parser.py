import json
import os
import re
from datetime import datetime

class LogParser:
    def __init__(self, source_dir, supported_formats, log_filter, batch_processor, encoding='utf-8'):
        self.source_dir = source_dir
        self.supported_formats = supported_formats
        self.log_filter = log_filter
        self.batch_processor = batch_processor
        self.encoding = encoding
        self.total_logs_processed = 0
        self.total_logs_after_filtering = 0
        self.total_errors_encountered = 0

    @staticmethod
    def remove_ansi_escape_sequences(line):
        """Removes ANSI escape sequences from a log line."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', line)

    def parse_json_log(self, log_lines):
        parsed_logs = []
        try:
            for line in log_lines:
                log_data = json.loads(line.strip())
                parsed_logs.append(log_data)
        except json.JSONDecodeError as e:
            self.total_errors_encountered += 1
            print(f"JSON parsing error: {e}")
        return parsed_logs

    def parse_plaintext_log(self, log_lines):
        parsed_logs = []
        # Preprocess logs to remove ANSI escape sequences
        cleaned_lines = [self.remove_ansi_escape_sequences(line.strip()) for line in log_lines if line.strip()]

        log_pattern = re.compile(
            r'\[v \d+\.\d+\.\d+/[0-9]+\]\s+(?P<source>[\w.]+)@(?P<level>[A-Z]+)\s+\|\s+(?P<timestamp>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{3})\(\d+\)>\s*(?P<message>.+)'
        )

        for line in cleaned_lines:
            match = log_pattern.match(line)
            if match:
                try:
                    timestamp = datetime.strptime(match.group('timestamp'), '%d/%m/%Y %H:%M:%S.%f')
                    log_entry = {
                        'timestamp': timestamp,
                        'source': match.group('source'),
                        'level': match.group('level'),
                        'message': match.group('message').strip(),
                    }
                    parsed_logs.append(log_entry)
                except Exception as e:
                    self.total_errors_encountered += 1
                    print(f"Error parsing timestamp in line: {line} - {e}")
            else:
                self.total_errors_encountered += 1
                print(f"Malformed log line: {line}")

        return parsed_logs

    def parse_logs(self, log_lines, log_format):
        if log_format == "JSON":
            return self.parse_json_log(log_lines)
        elif log_format == "PLAINTEXT":
            return self.parse_plaintext_log(log_lines)
        else:
            print(f"Unsupported log format: {log_format}")
            self.total_errors_encountered += 1
            return []

    def parse_file(self, file_path):
        try:
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as file:
                log_lines = file.readlines()

                # Detect format based on file extension or content
                log_format = self.detect_log_format(file_path)

                parsed_logs = self.parse_logs(log_lines, log_format)
                self.total_logs_processed += len(parsed_logs)

                # Filter and collect logs
                json_logs = []
                for log in parsed_logs:
                    if self.log_filter.is_within_date_range(log.get('timestamp')):
                        if self.log_filter.filter_log(log):
                            json_logs.append(log)
                            print(
                                f"Timestamp: {log['timestamp']}, "
                                f"Message: {log['message']}, "
                                f"source={log['source']}"
                            )
                            self.total_logs_after_filtering += 1
                            self.batch_processor.add_log(log)

                # Save logs to JSON
                json_file_path = "parsed_logs.json"
                try:
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(parsed_logs, json_file, indent=4, default=str)
                    print(f"Logs saved successfully to {json_file_path}")
                except Exception as e:
                    print(f"Error saving logs to file: {e}")

        except Exception as e:
            self.total_errors_encountered += 1
            print(f"Error reading file {file_path}: {e}")

    def detect_log_format(self, file_path):
        if file_path.lower().endswith('.json'):
            return "JSON"
        elif file_path.lower().endswith('.txt') or file_path.lower().endswith('.log'):
            return "PLAINTEXT"
        else:
            print(f"Unsupported file type for format detection: {file_path}")
            self.total_errors_encountered += 1
            return None

    def parse_all_logs(self):
        valid_extensions = (".json", ".log", ".txt")
        for root, _, files in os.walk(self.source_dir):
            for file_name in files:
                if file_name.lower().endswith(valid_extensions):
                    self.parse_file(os.path.join(root, file_name))
                else:
                    print(f"Skipping non-log file: {file_name}")

        print(f"\nTotal logs processed: {self.total_logs_processed}")
        print(f"Total logs after filtering: {self.total_logs_after_filtering}")
        print(f"Total errors encountered: {self.total_errors_encountered}")
