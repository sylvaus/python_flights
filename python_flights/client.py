import logging
import time
from datetime import datetime, timedelta
from itertools import product
from typing import List

import requests

from python_flights.itinerary import Itinerary
from python_flights.pods import Country, Currency, Airport, Place, Agent, Carrier, Direction, Trip, Segment, Price, \
    CabinClass, SortType, SortOrder

PARAM_DATE_FORMATTING = "%Y-%m-%d"
JSON_DATE_FORMATTING = "%Y-%m-%dT%H:%M:%S"

API_ADDRESS = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices"

LOCALES = [
    'de-DE', 'el-GR', 'en-GB', 'en-US', 'es-ES', 'es-MX', 'et-EE', 'fi-FI', 'fr-FR', 'hr-HR', 'hu-HU', 'id-ID', 'it-IT',
    'ja-JP', 'ko-KR', 'lt-LT', 'lv-LV', 'ms-MY', 'nb-NO', 'nl-NL', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'sk-SK',
    'sv-SE', 'th-TH', 'tr-TR', 'uk-UA', 'vi-VN', 'zh-CN', 'zh-HK', 'zh-SG', 'zh-TW'
]


class FlightBrowser:
    def __init__(self, api_key: str, locale="en-US", country="CA", currency="CAD"):
        self._get_headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': f"{api_key}"
        }
        self._post_headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': f"{api_key}",
            'content-type': "application/x-www-form-urlencoded"
        }
        self._locale = locale
        self._country = country
        self._currency = currency
        self._currencies = None
        self._logger = logging.getLogger(__name__ + "." + self.__class__.__name__)

    @property
    def currencies(self):
        if self._currencies is None:
            response = self._get(f"reference/v1.0/currencies")
            if response.status_code != 200:
                self._logger.warning(f"Request failed with status {response.status_code}")
                return []
            json = response.json()
            self._currencies = [
                Currency.from_json(currency_json)
                for currency_json in json.get("Currencies", [])
            ]
        return self._currencies

    @property
    def countries(self):
        response = self._get(f"reference/v1.0/countries/{self._locale}")
        if response.status_code != 200:
            return []
        json = response.json()

        return [
            Country.from_json(country_json)
            for country_json in json.get("Countries", [])
        ]

    def _get(self, url: str, params: dict = None):
        if params is None:
            params = {}

        return requests.get(f"{API_ADDRESS}/{url}", headers=self._get_headers, params=params)

    def _post(self, url: str, params: dict = None, data: str = ""):
        if params is None:
            params = {}

        return requests.post(
            f"{API_ADDRESS}/{url}", headers=self._post_headers
            , params=params, data=data
        )

    def get_airports(self, keyword):
        response = self._get(
            f"autosuggest/v1.0/{self._country}/{self._currency}/{self._locale}/"
            , params={"query": f"{keyword}"}
        )
        if response.status_code != 200:
            return []

        response_json = response.json()
        return [
            Airport.from_json(airport_json)
            for airport_json in response_json.get("Places", [])
        ]

    def get_flights(
            self, departure_date: datetime, departure_id: str
            , arrival_date: datetime, arrival_id: str
            , cabin_class: CabinClass = None
            , adults: int = 1, children: int = 0
            , infants: int = 0, stops: int = None
            , duration_mins: int = None, number_results: int = 10
            , sort_type: SortType = None, sort_order: SortOrder = SortOrder.ASCENDING
    ) -> List[Itinerary]:
        params = \
            f"inboundDate={arrival_date.strftime(PARAM_DATE_FORMATTING)}" \
                f"&country={self._country}&currency={self._currency}" \
                f"&locale={self._locale}&originPlace={departure_id}-sky&destinationPlace={arrival_id}-sky" \
                f"&outboundDate={departure_date.strftime(PARAM_DATE_FORMATTING)}" \
                f"&adults={adults}&children={children}&infants={infants}"

        if cabin_class:
            params += f"&cabinClass={cabin_class.value}"

        self._logger.debug(f"Creating session with parameters {params}")
        response = self._post("pricing/v1.0", data=params)
        if response.status_code != 201:
            return []

        _, url = response.headers["Location"].split("/apiservices/")

        params = {"pageIndex": "0", "pageSize": f"{number_results}"}
        if duration_mins:
            params["duration"] = f"{duration_mins}"
        if stops:
            params["stops"] = f"{stops}"
        if sort_type:
            params["sortType"] = f"{sort_type.value}"
            params["sortOrder"] = f"{sort_order.value}"

        self._logger.debug("Polling session")
        response = self._get(url, params)
        if response.status_code != 200:
            return []

        return self._extract_itineraries(response.json())

    def _extract_itineraries(self, response_json) -> List[Itinerary]:
        currencies = [
            Currency.from_json(json_dict)
            for json_dict in response_json.get("Currencies", [])
        ]
        id_places = {
            json_dict["Id"]: Place.from_json(json_dict)
            for json_dict in response_json.get("Places", [])
        }
        id_agents = {
            json_dict["Id"]: Agent.from_json(json_dict)
            for json_dict in response_json.get("Agents", [])
        }
        id_carriers = {
            json_dict["Id"]: Carrier.from_json(json_dict)
            for json_dict in response_json.get("Carriers", [])
        }
        id_segments = {}
        for json_dict in response_json.get("Segments", []):
            id_ = json_dict["Id"]
            departure_place = id_places[json_dict["DestinationStation"]]
            departure_time = datetime.strptime(json_dict["DepartureDateTime"], JSON_DATE_FORMATTING)
            arrival_place = id_places[json_dict["OriginStation"]]
            arrival_time = datetime.strptime(json_dict["ArrivalDateTime"], JSON_DATE_FORMATTING)
            carrier = id_carriers[json_dict["Carrier"]]
            operating_carrier = id_carriers[json_dict["OperatingCarrier"]]
            duration = timedelta(minutes=json_dict["Duration"])
            flight_number = json_dict["FlightNumber"]
            trip_type = json_dict["JourneyMode"]
            direction = Direction.OUTBOUND if json_dict["Directionality"] == "Outbound" else Direction.INBOUND
            id_segments[id_] = Segment(
                id_, departure_place, departure_time, arrival_place, arrival_time,
                carrier, operating_carrier, duration, flight_number, trip_type, direction
            )

        id_trips = {}
        for json_dict in response_json.get("Legs", []):
            id_ = json_dict["Id"]
            segments = [
                id_segments[segment_id]
                for segment_id in json_dict.get("SegmentIds", [])
            ]
            departure_place = id_places[json_dict["DestinationStation"]]
            departure_date = datetime.strptime(json_dict["Departure"], JSON_DATE_FORMATTING)
            arrival_place = id_places[json_dict["OriginStation"]]
            arrival_date = datetime.strptime(json_dict["Arrival"], JSON_DATE_FORMATTING)
            duration = timedelta(minutes=json_dict["Duration"])
            stops = [
                id_places[place_id]
                for place_id in json_dict.get("Stops", [])
            ]
            carriers = [
                id_carriers[carrier_id]
                for carrier_id in json_dict.get("Carriers", [])
            ]
            operating_carriers = [
                id_carriers[carrier_id]
                for carrier_id in json_dict.get("Carriers", [])
            ]
            direction = Direction.OUTBOUND if json_dict["Directionality"] == "Outbound" else Direction.INBOUND
            id_trips[id_] = Trip(
                id_, segments, departure_place, departure_date, arrival_place, arrival_date
                , duration, stops, carriers, operating_carriers, direction
            )

        itineraries = []
        for json_dict in response_json.get("Itineraries", []):
            outbound_trip = id_trips[json_dict["OutboundLegId"]]
            inbound_trip = id_trips[json_dict["InboundLegId"]]
            prices = []
            for price_dict in json_dict.get("PricingOptions", []):
                agents = [id_agents[agent_id] for agent_id in price_dict["Agents"]]
                quote_age = timedelta(minutes=price_dict["QuoteAgeInMinutes"])
                price = price_dict["Price"]
                url = price_dict["DeeplinkUrl"]
                prices.append(Price(agents, quote_age, price, url))
            itineraries.append(Itinerary(outbound_trip, inbound_trip, prices))

        return itineraries

    def get_flights_ranges(
            self, departure_dates: List[datetime], departure_ids: List[str]
            , arrival_dates: List[datetime], arrival_ids: List[str]
            , *args, rate_limit_per_min: int = 40, **kwargs
    ) -> List[Itinerary]:
        itineraries = []
        # The time in between calls is multiplied by two because two requests are made to get flights
        in_between_call_s = (60 / rate_limit_per_min) * 2
        combinations = list(product(departure_dates, departure_ids, arrival_dates, arrival_ids))
        nb_combinations = len(combinations)
        for index, (departure_date, departure_id, arrival_date, arrival_id) in enumerate(combinations):
            self._logger.debug(f"Getting itineraries {index} out of {nb_combinations}")

            start_time = time.time()
            itineraries.extend(
                self.get_flights(departure_date, departure_id, arrival_date, arrival_id, *args, **kwargs)
            )

            time.sleep(max([0, in_between_call_s - (time.time() - start_time)]))

        return itineraries
