# -*- coding: utf-8 -*-
"""A module that polls the database for current exchange rates"""
from features.database_operations import DatabaseReadonlyUser
import math


class DisplayExchangeRate:
    """Class that performs operations on database. Starting point.

    - `selected_currency` -- returns exchange rates for selected currency in specific period
    - `currency_conversion` -- establishing database connection
    """
    __db_connect = DatabaseReadonlyUser()

    @staticmethod
    def __make_me_json(method_data: tuple) -> dict:
        """Parses the tuple into the dictionary

        Args:
            method_data: a tuple containing currency, code, bid, ask and date

        Returns:
              dict with selected exchange rates data
        """
        return {'Rates': [{'currency': currency[0], 'code': currency[1], 'bid': currency[2],
                          'ask': currency[3], 'date': currency[4].strftime("%d/%m/%Y")} for currency in method_data]}

    @classmethod
    def selected_currency(cls, currency, date_from, date_to) -> dict:
        """Returns exchange rates for selected currency in specific period.

        Args:
            currency: selected currency
            date_from: datatime.date - specifies the date range
            date_to: datatime.date - specifies the date range

        Returns:
            a dictionary containing information about exchange rates from a specific period
        """
        return cls.__make_me_json(cls.__db_connect.select_where(currency, date_from, date_to))

    @classmethod
    def currency_conversion(cls, currency_from, currency_to, value, date):
        """Converting an exchange rate based on a given amount.

        Args:
            currency_from: the currency with which we are making the exchange
            currency_to: the currency we exchange for
            value: value we exchange
            date: which day we take the course

        Returns:
            dictionary with new value and change from exchange.
        """
        if currency_from == "PLN":
            exchange_rate_from = ('PLN', '1')
        else:
            exchange_rate_from = cls.__db_connect.select_where(currency_from, date, date)[0][1:3]
        if currency_to == "PLN":
            exchange_rate_to = ('PLN', '1')
        else:
            exchange_rate_to = cls.__db_connect.select_where(currency_to, date, date)[0][1:4:2]
        currency_from, currency_to, value = float(exchange_rate_from[1]), float(exchange_rate_to[1]), float(value)
        pln = value * currency_from
        new_value = pln//currency_to
        change = (pln - new_value * currency_to)/currency_from
        new_value = f'{new_value} {exchange_rate_to[0]}'
        change = f'{math.floor(change*100)/100} {exchange_rate_from[0]}'
        return {"New value": new_value, "Change": change}
