from log_processor.log_parser import LogParser

parser = LogParser()
parsed_logs = parser.parse_log("2024-03-27 12:00:00 ERROR MainClass - Something went wrong")
print(parsed_logs)
