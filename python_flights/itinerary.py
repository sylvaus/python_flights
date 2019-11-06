from dataclasses import dataclass
from typing import List

from python_flights.pods import Trip, Price


@dataclass
class Itinerary:
    outbound_trip: Trip
    inbound_trip: Trip
    price_options: List[Price]

    @property
    def min_price(self):
        return min((price.price for price in self.price_options))

    @property
    def total_duration(self):
        return self.outbound_trip.duration + self.inbound_trip.duration

    @property
    def outbound_duration(self):
        return self.outbound_trip.duration

    @property
    def inbound_duration(self):
        return self.inbound_trip.duration
