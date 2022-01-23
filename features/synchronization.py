# -*- coding: utf-8 -*-
"""Module responsible for saving new data to PostgreSQL.

Checks the date of the last synchronization, downloads the current exchange rates from the NBP,
and then initiates saving it to database.
"""
from requests import get
from features.database_operations import DatabaseSyncUser
from features.datetime_operations import datetime_converter


class DataSynchronization:
    """Module responsible for saving new data to PostgreSQL.

    - `start_synchronization` -- Initiates synchronization of the current exchange rates.
    """
    __currency_table = get('http://api.nbp.pl/api/exchangerates/tables/C?format=json').json()[0]['rates']
    __db_connect = DatabaseSyncUser()

    @classmethod
    def __check_last_sync_date(cls):
        """Checks what is the last synchronization date in the database.

        Returns:
            datetime.date or None (if there is no previous sync data)
        """
        try:
            last_sync_date = str(cls.__db_connect.download_date())
        except IndexError:
            print('No data from previous sync.')
            return None
        return datetime_converter(last_sync_date)

    @classmethod
    def start_synchronization(cls, new_sync_date) -> None:
        """Initiates synchronization of the current exchange rates with database.

        Args:
            new_sync_date: synchronization date in datetime.date type

        Raises:
            AssertionError: today synchronization date or last synchronization date had unexpected data
        """
        last_sync_date = cls.__check_last_sync_date()
        if new_sync_date == last_sync_date:
            pass
        elif last_sync_date is None or last_sync_date < new_sync_date:
            cls.__currency_data_dump(new_sync_date)
        else:
            raise AssertionError('DataSynchronization.start_synchronization: Unexpected values.')

    @classmethod
    def __currency_data_dump(cls, new_sync_date) -> None:
        """Initiates saving data from the current synchronization to the database.

        Args:
            new_sync_date: synchronization date in datetime.date type
        """
        for table_value in cls.__currency_table:
            actual_currency = [value for key, value in table_value.items()]
            actual_currency.append(new_sync_date)
            cls.__db_connect.insert_data(tuple(actual_currency))
