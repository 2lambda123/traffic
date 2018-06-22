import logging
import pickle
import re
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple, Optional

import requests
from cartopy.crs import PlateCarree

from ...core.mixins import ShapelyMixin


class AirportNamedTuple(NamedTuple):

    alt: int
    country: str
    iata: str
    icao: str
    lat: float
    lon: float
    name: str


class Airport(AirportNamedTuple, ShapelyMixin):

    def __repr__(self):
        return (
            f"{self.icao}/{self.iata}    {self.name.strip()} ({self.country})"
            f"\n\t{self.lat} {self.lon} altitude: {self.alt}"
        )

    def _repr_html_(self):
        title = f"<b>{self.name.strip()}</b> ({self.country}) "
        title += f"<code>{self.icao}/{self.iata}</code>"
        no_wrap_div = '<div style="white-space: nowrap">{}</div>'
        return title + no_wrap_div.format(self._repr_svg_())

#    @property
#    def extent(self):
#         not so bad balance for common usecases...
#        return (self.lon - 1, self.lon + 1, self.lat - .7, self.lat + .7)

    @lru_cache()
    def osm_request(self):
        from cartotools.osm import request, tags
        return request(
            (self.lon - .06, self.lat - .06, self.lon + .06, self.lat + .06),
            **tags.airport,
        )

    @property
    def shape(self):
        return self.osm_request().shape

    def plot(self, ax, **kwargs):
        params = {
            "edgecolor": "steelblue",
            "facecolor": "None",
            "crs": PlateCarree(),
            **kwargs,
        }
        ax.add_geometries(list(self.osm_request()), **params)


class AirportParser(object):

    cache: Optional[Path] = None

    def __init__(self):
        if self.cache is not None and self.cache.exists():
            with open(self.cache, "rb") as fh:
                self.airports = pickle.load(fh)
        else:
            c = requests.get("https://www.flightradar24.com/_json/airports.php",
                             headers={"user-agent": "Mozilla/5.0"})
            self.airports = list(Airport(**a) for a in c.json()["rows"])

            logging.info("Caching airport list from FlightRadar")
            if self.cache is not None:
                with open(self.cache, "wb") as fh:
                    pickle.dump(self.airports, fh)

    def __getitem__(self, name: str):
        return next(
            (
                a
                for a in self.airports
                if (a.iata == name.upper()) or (a.icao == name.upper())
            ),
            None,
        )

    def search(self, name: str):
        return list(
            (
                a
                for a in self.airports
                if (a.iata == name.upper())
                or (a.icao == name.upper())
                or (re.match(name, a.country, flags=re.IGNORECASE))
                or (re.match(name, a.name, flags=re.IGNORECASE))
            )
        )
