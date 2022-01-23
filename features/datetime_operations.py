# -*- coding: utf-8 -*-
"""Wrapper for datetime module."""
from datetime import datetime, timedelta


def datetime_timedelta(days: int = 7) -> timedelta:
    """Prepare an object representing difference between two dates.


    Args:
        days: number of days that should be converted into timedelta object

    Returns:
        timedelta: object representing the number of days
    """
    return timedelta(days=days)


def today() -> datetime.date:
    """Return the current local date.

    Returns:
        datetime.date: current local date (year-month-day)
    """
    return datetime.today().date()


def datetime_converter(date_string: str) -> datetime.date:
    """Return a datetime corresponding to date_string.

    Return a datetime corresponding to date_string parsed. Default format: year-month-day.

    Args:
        date_string: string containing date to be parsed

    Returns:
        datetime.date: string converted into datatime.date format
    """
    return datetime.strptime(date_string, '%Y-%m-%d').date()
