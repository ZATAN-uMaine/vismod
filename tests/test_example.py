import unittest

# Just an example test to show how it works
# Run with `hatch test`


class TestExample(unittest.TestCase):
    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")
