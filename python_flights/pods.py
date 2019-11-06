from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import Enum
from typing import List


class Direction(Enum):
    OUTBOUND = "Outbound"
    INBOUND = "Inbound"


class CabinClass(Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premiumeconomy"
    BUSINESS = "business"
    FIRST = "first"


class SortType(Enum):
    CARRIER = "carrier"
    DURATION = "duration"
    OUT_ARRIVE_TIME = "outboundarrivetime"
    OUT_DEPART_TIME = "outbounddeparttime"
    IN_ARRIVE_TIME = "inboundarrivetime"
    IN_DEPART_TIME = "inbounddeparttime"
    PRICE = "price"


class SortOrder(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


@dataclass
class Country:
    code: str
    name: str

    @staticmethod
    def from_json(json_dict: dict):
        return Country(json_dict["Code"], json_dict["Name"])


@dataclass
class Currency:
    code: str
    symbol: str

    @staticmethod
    def from_json(json_dict: dict):
        return Currency(json_dict["Code"], json_dict["Symbol"])


@dataclass
class Airport:
    place_id: str
    place_name: str
    country_id: str
    region_id: str
    city_id: str
    country_name: str

    @staticmethod
    def from_json(json_dict: dict):
        return Airport(
            json_dict["PlaceId"], json_dict["PlaceName"]
            , json_dict["CountryId"], json_dict["RegionId"]
            , json_dict["CityId"], json_dict["CountryId"]
        )


@dataclass
class Place:
    id: int
    parent_id: str
    code: str
    type: str
    city: str

    @staticmethod
    def from_json(json_dict: dict):
        return Place(
            json_dict["Id"], json_dict.get("ParentId", None), json_dict["Code"], json_dict["Type"], json_dict["Name"]
        )


@dataclass
class Agent:
    id: int
    name: str
    url: str
    status: str
    type: str

    @staticmethod
    def from_json(json_dict: dict):
        return Place(
            json_dict["Id"], json_dict["Name"], json_dict["ImageUrl"], json_dict["Status"], json_dict["Type"]
        )


@dataclass
class Carrier:
    id: int
    code: str
    name: str
    image_url: str
    display_code: str

    @staticmethod
    def from_json(json_dict: dict):
        return Place(
            json_dict["Id"], json_dict["Code"], json_dict["Name"]
            , json_dict["ImageUrl"], json_dict["DisplayCode"]
        )


@dataclass
class Price:
    agents: List[Agent]
    quote_age: timedelta
    price: float
    url: str


@dataclass
class Segment:
    id: int
    departure_place: Place
    departure_date: datetime
    arrival_place: Place
    arrival_date: datetime
    carrier: Carrier
    operating_carrier: Carrier
    duration: timedelta
    flight_number: str
    segment_type: str
    direction: Direction


@dataclass
class Trip:
    id: str
    segments: List[Segment]
    departure_place: Place
    departure_date: datetime
    arrival_place: Place
    arrival_date: datetime
    duration: timedelta
    stops: List[Place]
    carriers: List[Carrier]
    operating_carriers: List[Carrier]
    direction: Direction
