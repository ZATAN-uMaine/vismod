import logging
from datetime import datetime, timedelta, timezone
from dateutil import parser as dparser
from math import floor


def parse_dates(start, end):
    """
    Validates that dates are in correct ISO 8086 format,
    and represent a reasonable date range.
    Returns False if there is a problem, otherwise return
    a tuple of datetimes
    """
    try:
        parsed_start = dparser.parse(start)
        parsed_end = dparser.parse(end)
        # make the new date a bit in the future just to be safe
        now = datetime.now().replace(
            tzinfo=timezone(offset=timedelta(hours=0))
        ) + timedelta(
            hours=1
        )  # noqa
        if now < parsed_end:
            logging.warning(f"date {end} appears to be in the future")
            return False
        if parsed_start > parsed_end:
            logging.warning(f"Start date {start} is after end date {end}")
            return False
        return (parsed_start, parsed_end)
    except ValueError:
        logging.warning(
            f"Could not read date strings {start} and {end} as ISO 8086"
        )
        return False
    except TypeError:
        logging.warning(
            f"Could not read date strings {start} and {end} as ISO 8086"
        )
        return False


def get_aggregation_interval(start: datetime, end: datetime, points=300):
    """
    Given a start date and an end date,
    divide it into $points intervals of N seconds.
    Return N.

    This is used to set a reasonable aggregation window in Plotly.
    """
    diff = (end - start).total_seconds()
    interval = diff / points
    iinterval = floor(interval)
    if iinterval < 60:
        return 60
    return iinterval
