import unittest

def assert_json(self, response):
    self.assertEqual(response.content_type, 'application/json')

def assert_success(self, response):
    self.assertEqual(response.status_int, 200)

def assert_error(self, response, error_code=404):
    self.assertEqual(response.status_int, error_code)
