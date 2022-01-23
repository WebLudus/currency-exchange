# General info
An application that downloads the current exchange rate from the NBP and saves them to the non-volatile memory. Then, through the REST API, it displays the current exchange rate of a given currency or currencies (where the reference point is PLN). The rate is saved in the memory for no longer than 7 days and ignores the lack of updates in the NPB API (exchange rates are not updated every day).
In addition, it offers the possibility of currency exchange for a specified amount, according to the exchange rate at the National Bank of Poland.

## Technologies
* Python 3.10,
* PostgreSQL,
* Flask.

## Usage
### GET /api/currency
##### Query Params
* date_from = yyyy-mm-dd
* date_to = yyyy-mm-dd
* currency_code = USD | USD-EUR
#### Response:
```
{
    "Rates": [
        {
            "ask": "string",
            "bid": "string",
            "code": "string",
            "currency": "string",
            "date": "string"
        },
        {
            "ask": "string",
            "bid": "string",
            "code": "string",
            "currency": "string",
            "date": "string"
        }
    ]
}
```


### GET /api/currency/exchange
#### Body
```
{
    "currency_from": "string",
    "currency_to": "string",
    "value": "string"
}
```

#### Response
```
{
    "Change": "string",
    "New value": "string"
}
```
