Python Flights
==============
Introduction
--------------
This python package provides a small wrapper around the RapidAPI interface to SkyScanner API

Basic Usage
-----------
To use the functions provided by Python Flights you will need to get an API key from RapidAPI: [link](https://rapidapi.com/)
```python
from datetime import datetime

from python_flights.client import FlightBrowser

API_KEY = "YOUR_API_KEY"

browser = FlightBrowser(API_KEY)
# Print all currencies available
print(browser.currencies) 
# Print all airports having the Montreal keyword
print(browser.get_airports("Montreal"))
# Get itineraries matching the given dates from Porto airport and Bangkok airport
itineraries = browser.get_flights(datetime(year=2020, month=1, day=12), "OPO", datetime(year=2020, month=1, day=24) , "BKK")
```

TODO
----
* Add docstring to all functions
* Add helper methods to the different containers
