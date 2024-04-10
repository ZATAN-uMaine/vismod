import logging
from datetime import datetime, timedelta, timezone


def validate_dates(start, end):
    """
    Validates that dates are in correct ISO 8086 format,
    and represent a reasonable date range.
    Returns true if we're all good.
    """
    try:
        parsed_start = datetime.fromisoformat(start)
        parsed_end = datetime.fromisoformat(end)
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
    except ValueError:
        logging.warning(
            f"Could not read date strings {start} and {end} as ISO 8086"
        )
        return False
    return True
