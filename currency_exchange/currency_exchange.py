# -*- coding: utf-8 -*-
"""An API-controlled currency exchange office."""
from flask import Flask, request
from flask_restful import Api
from readonly_user import DisplayExchangeRate
from features.datetime_operations import today
from features.synchronization import DataSynchronization
from features.clean_old_data import delete_old_data

app = Flask(__name__)
api = Api(app)


def convert_string_to_tuple(items_joined_by_a_dash: str) -> tuple:
    """Converts a string containing multiple items joined together by a dash to a tuple.

    Args:
        items_joined_by_a_dash: a sequence of words connected with dashes

    Returns:
        tuple with parsed words
    """
    return tuple(map(str, items_joined_by_a_dash.replace('-', ', ').split(', ')))


@app.route('/api/currency', methods=['GET'])
@app.route('/api/currency/<days>', methods=['GET'])
def currency_data(days: str | None = None):
    """Endpoint that returns information about currency exchange rates.

    Returns information about exchange rates.
    Takes 3 arguments (date_from, date_to, and currency_code) which enable it to obtain a precise answer.

    Args:
         days: str('today') | None - specifies a date range

    Responses:
        200:
            returns information about the exchange rate
        404:
            an invalid value was entered in the days field
    """
    currency_code = request.args.get('currency_code')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    if days == 'today':
        date_from = today()
        date_to = date_from
    elif days is not None:
        return '', 404
    try:
        if '-' in currency_code:
            currency_code = convert_string_to_tuple(currency_code)
    except TypeError:
        pass
    return DisplayExchangeRate.selected_currency(currency_code, date_from, date_to)


@app.route('/api/currency/exchange', methods=['POST'])
def currency_exchange():
    """The endpoint that initiates the module responsible for currency exchange.

    Responses:
        200:
            {
                "Change": "string",
                "New value": "string"
            }
    """
    request_data = request.get_json()
    currency_from, currency_to = request_data['currency_from'], request_data['currency_to']
    value = request_data['value']
    return DisplayExchangeRate.currency_conversion(currency_from, currency_to, value, today())


if __name__ == '__main__':
    DataSynchronization.start_synchronization(today())
    delete_old_data()
    app.run()
