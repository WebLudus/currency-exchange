# -*- coding: utf-8 -*-
"""Module responsible for cleaning old data from PostgreSQL."""
from features.database_operations import DatabaseCleaningUser
from features.datetime_operations import today, datetime_timedelta


def delete_old_data() -> None:
    """Initiates the deletion of data from sync older than a week."""
    db_connect = DatabaseCleaningUser()
    db_connect.delete_old_data(today()-datetime_timedelta())
