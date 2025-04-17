import json
import os
import re
from datetime import datetime


def remove_ansi_escape_sequences(text):
    """Removes ANSI escape codes from log text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


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

    def parse_json_log(self, log_lines):
        parsed_logs = []
        for line in log_lines:
            try:
                log_data = json.loads(line.strip())
                parsed_logs.append(log_data)
            except json.JSONDecodeError as e:
                self.total_errors_encountered += 1
                print(f"JSON parsing error: {e} - Line: {line.strip()}")
        return parsed_logs

    def parse_plaintext_log(self, log_lines):
        parsed_logs = []
        cleaned_lines = [remove_ansi_escape_sequences(line.strip()) for line in log_lines if line.strip()]

        log_pattern = re.compile(
            r'\[v \d+\.\d+\.\d+/[0-9]+\] (?P<source>[a-zA-Z0-9._]+)\.(?P<process_id>\d+)@(?P<level>[A-Z]+) \| '
            r'(?P<timestamp>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d+)\(\d+\)>\s*(?P<message>.+)'
        )

        exception_pattern = re.compile(r'Exception in thread|Caused by:')
        stack_trace_pattern = re.compile(r'\s+at\s+[a-zA-Z0-9._]+\([^)]*\)')

        last_log = None

        for line in cleaned_lines:
            match = log_pattern.match(line)
            if match:
                try:
                    timestamp = datetime.strptime(match.group('timestamp'), '%d/%m/%Y %H:%M:%S.%f')
                    log_entry = {
                        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'),
                        'source': match.group('source'),
                        'process_id': match.group('process_id'),
                        'level': match.group('level'),
                        'message': match.group('message').strip(),
                    }
                    parsed_logs.append(log_entry)
                    last_log = log_entry
                    print(f"? Successfully parsed log: {log_entry}")
                except Exception as e:
                    self.total_errors_encountered += 1
                    print(f"? Error parsing timestamp in line: {line} - {e}")
            elif last_log and (exception_pattern.match(line) or stack_trace_pattern.match(line)):
                last_log["message"] += f"\n{line}"
                print(f"? Appended exception/stack trace to previous log: {line}")
            else:
                self.total_errors_encountered += 1
                print(f"?? Skipped malformed log line: {line}")

        return parsed_logs

    def parse_logs(self, log_lines, log_format):
        if log_format.lower() == "json":
            return self.parse_json_log(log_lines)
        elif log_format.lower() == "plaintext":
            return self.parse_plaintext_log(log_lines)
        else:
            print(f"Unsupported log format: {log_format}")
            self.total_errors_encountered += 1
            return []

    def parse_file(self, file_path):
        try:
            print(f"? Processing file: {file_path}")
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as file:
                log_lines = file.readlines()
            print(f"? Read {len(log_lines)} lines from {file_path}")

            log_format = self.detect_log_format(file_path)
            if not log_format:
                return

            parsed_logs = self.parse_logs(log_lines, log_format)
            self.total_logs_processed += len(parsed_logs)
            print(f"? Total parsed logs: {len(parsed_logs)}")

            json_file_path = "parsed_logs.json"
            try:
                existing_logs = []
                if os.path.exists(json_file_path):
                    with open(json_file_path, 'r', encoding='utf-8') as json_file:
                        try:
                            existing_logs = json.load(json_file)
                        except json.JSONDecodeError:
                            existing_logs = []

                existing_logs.extend(parsed_logs)

                with open(json_file_path, 'w', encoding='utf-8') as json_file:
                    json.dump(existing_logs, json_file, indent=4, default=str)
                print(f"? Logs appended successfully to {json_file_path}")
            except Exception as e:
                print(f"Error saving logs to file: {e}")

        except Exception as e:
            self.total_errors_encountered += 1
            print(f"Error reading file {file_path}: {e}")

    def detect_log_format(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".json":
            return "json"
        elif file_extension in [".txt", ".log"]:
            return "plaintext"
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
        print(f"Total errors encountered: {self.total_errors_encountered}")
