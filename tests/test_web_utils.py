import unittest

from vismod_web.utils import parse_dates


class TestPreProcessor(unittest.TestCase):
    def test_invalid_dates(self):
        # not dates
        self.assertFalse(parse_dates("ASDFASDF", "ASDFASDF"))
        # not in ISO8086 format
        self.assertFalse(parse_dates("3/30/2024", "4/1/2024"))
        self.assertFalse(parse_dates("3/30/2024 10:50", "4/1/2024 11:20"))
        # start is after end
        self.assertFalse(
            parse_dates("2024-04-06T15:30:00Z", "2024-04-05T15:30:00Z")
        )

    def test_valid_dates(self):
        # produced from the web ui
        self.assertTrue(
            parse_dates(
                "2024-03-30T19:54:07.513+04:00",
                "2024-04-06T19:54:07.513+04:00",  # noqa
            )
        )

        self.assertTrue(
            parse_dates(
                "2024-04-03T17:08:55.063Z", "2024-04-10T17:08:55.063Z"
            )
        )
