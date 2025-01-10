import unittest
from datetime import datetime
from filters import LogFilter

class TestLogFilter(unittest.TestCase):

    def setUp(self):
        self.include_keywords = ["error", "fail"]
        self.exclude_keywords = ["ignore", "test"]
        self.date_range = {"start": "2023-01-01", "end": "2023-12-31"}
        self.log_filter = LogFilter(self.include_keywords, self.exclude_keywords, self.date_range)

    def test_is_within_date_range(self):
        log_date = datetime.strptime("2023-06-15", "%Y-%m-%d")
        self.assertTrue(self.log_filter.is_within_date_range(log_date))

        log_date = datetime.strptime("2022-12-31", "%Y-%m-%d")
        self.assertFalse(self.log_filter.is_within_date_range(log_date))

    def test_filter_log(self):
        log_entry = {"message": "This is an error message"}
        self.assertTrue(self.log_filter.filter_log(log_entry))

        log_entry = {"message": "This is a test message"}
        self.assertFalse(self.log_filter.filter_log(log_entry))

    def test_filter_by_level(self):
        log_entry = {"level": "ERROR"}
        self.assertTrue(self.log_filter.filter_by_level(log_entry))

        log_entry = {"level": "INFO"}
        self.assertFalse(self.log_filter.filter_by_level(log_entry))

if __name__ == '__main__':
    unittest.main()
import unittest
from datetime import datetime
from filters import LogFilter

class TestLogFilter(unittest.TestCase):

    def setUp(self):
        self.include_keywords = ["error", "fail"]
        self.exclude_keywords = ["ignore", "test"]
        self.date_range = {"start": "2023-01-01", "end": "2023-12-31"}
        self.log_filter = LogFilter(self.include_keywords, self.exclude_keywords, self.date_range)

    def test_is_within_date_range(self):
        log_date = datetime.strptime("2023-06-15", "%Y-%m-%d")
        self.assertTrue(self.log_filter.is_within_date_range(log_date))

        log_date = datetime.strptime("2022-12-31", "%Y-%m-%d")
        self.assertFalse(self.log_filter.is_within_date_range(log_date))

    def test_filter_log(self):
        log_entry = {"message": "This is an error message"}
        self.assertTrue(self.log_filter.filter_log(log_entry))

        log_entry = {"message": "This is a test message"}
        self.assertFalse(self.log_filter.filter_log(log_entry))

    def test_filter_by_level(self):
        log_entry = {"level": "ERROR"}
        self.assertTrue(self.log_filter.filter_by_level(log_entry))

        log_entry = {"level": "INFO"}
        self.assertFalse(self.log_filter.filter_by_level(log_entry))

if __name__ == '__main__':
    unittest.main()