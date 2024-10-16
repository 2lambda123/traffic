from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Set, Type, TypeVar
from xml.etree import ElementTree

import pandas as pd

from ....core.mixins import DataFrameMixin
from ....core.time import timelike, to_datetime
from .reply import B2BReply
from .xml import REQUESTS

rename_cols = {"id": "tvId", "regulationState": "state", "subType": "type"}

default_regulation_fields: Set[str] = {
    "applicability",
    # "autolink",
    # "measureCherryPicked",
    # "initialConstraints",
    # "linkedRegulations",
    "location",
    "protectedLocation",
    "reason",
    # "remark",
    "regulationState",
    # "supplementaryConstraints",
    # "lastUpdate",
    # "noDelayWindow",
    # "updateCapacityRequired",
    # "updateTVActivationRequired",
    # "externallyEditable",
    "subType",
    # "delayTVSet",
    # "createdByFMP",
    # "sourceHotspot",
    # "mcdmRequired",
    # "dataId",
    # "scenarioReference",
    # "delayConfirmationThreshold",
}

# https://github.com/python/mypy/issues/2511
RegulationListTypeVar = TypeVar("RegulationListTypeVar", bound="RegulationList")


class RegulationInfo(B2BReply):
    @property
    def regulation_id(self) -> str:
        assert self.reply is not None
        elt = self.reply.find("regulationId")
        assert elt is not None
        assert elt.text is not None
        return elt.text

    @property
    def state(self) -> str:
        assert self.reply is not None
        elt = self.reply.find("regulationState")
        assert elt is not None
        assert elt.text is not None
        return elt.text

    @property
    def type(self) -> str:
        assert self.reply is not None
        elt = self.reply.find("subType")
        assert elt is not None
        assert elt.text is not None
        return elt.text

    @property
    def start(self) -> pd.Timestamp:
        assert self.reply is not None
        elt = self.reply.find("applicability/wef")
        assert elt is not None
        assert elt.text is not None
        return pd.Timestamp(elt.text, tz="UTC")

    @property
    def stop(self) -> pd.Timestamp:
        assert self.reply is not None
        elt = self.reply.find("applicability/unt")
        assert elt is not None
        assert elt.text is not None
        return pd.Timestamp(elt.text, tz="UTC")

    @property
    def tvId(self) -> str:
        assert self.reply is not None
        elt = self.reply.find("location/id")
        assert elt is not None
        assert elt.text is not None
        return elt.text

    @property
    def location(self) -> Optional[str]:
        assert self.reply is not None
        elt = self.reply.find(
            "location/referenceLocation-ReferenceLocationAirspace/id"
        )
        if elt is not None:
            return elt.text
        elt = self.reply.find(
            "location/referenceLocation-ReferenceLocationAerodrome/id"
        )
        if elt is not None:
            return elt.text
        return None

    @property
    def fl_min(self) -> int:
        assert self.reply is not None
        elt = self.reply.find("location/flightLevels/min/level")
        return int(elt.text) if elt is not None and elt.text is not None else 0

    @property
    def fl_max(self) -> int:
        assert self.reply is not None
        elt = self.reply.find("location/flightLevels/max/level")
        return (
            int(elt.text) if elt is not None and elt.text is not None else 999
        )

    def __getattr__(self, name: str) -> str:
        cls = type(self)
        assert self.reply is not None
        elt = self.reply.find(name)
        if elt is not None:
            return elt.text  # type: ignore
        msg = "{.__name__!r} object has no attribute {!r}"
        raise AttributeError(msg.format(cls, name))


class RegulationList(DataFrameMixin, B2BReply):
    columns_options = dict(
        regulationId=dict(style="blue bold"),
        state=dict(),
        type=dict(),
        reason=dict(),
        start=dict(),
        stop=dict(),
        tvId=dict(),
        airspace=dict(),
        aerodrome=dict(),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 0 and "data" not in kwargs:
            super().__init__(data=None, **kwargs)
        else:
            super().__init__(*args, **kwargs)

    @classmethod
    def fromB2BReply(
        cls: Type[RegulationListTypeVar], r: B2BReply
    ) -> RegulationListTypeVar:
        assert r.reply is not None
        return cls.fromET(r.reply)

    @classmethod
    def fromET(
        cls: Type[RegulationListTypeVar], tree: ElementTree.Element
    ) -> RegulationListTypeVar:
        instance = cls()
        instance.reply = tree
        instance.build_df()
        return instance

    def __getitem__(self, item: str) -> Optional[RegulationInfo]:
        assert self.reply is not None
        for elt in self.reply.findall("data/regulations/item"):
            key = elt.find("regulationId")
            assert key is not None
            if key.text == item:
                return RegulationInfo.fromET(elt)

        return None

    def _ipython_key_completions_(self) -> Set[str]:
        return set(self.data.RegulationId.unique())

    def build_df(self) -> None:
        assert self.reply is not None

        refloc = "location/referenceLocation-"

        self.data = pd.DataFrame.from_records(
            [
                {
                    **{p.tag: p.text for p in elt if p.text is not None},
                    **{
                        p.tag: p.text
                        for p in elt.find("location")  # type: ignore
                        if p.text is not None
                    },
                    **{
                        "start": (
                            elt.find("applicability/wef").text  # type: ignore
                            if elt.find("applicability") is not None
                            else None
                        ),
                        "stop": (
                            elt.find("applicability/unt").text  # type: ignore
                            if elt.find("applicability") is not None
                            else None
                        ),
                    },
                    **{
                        "airspace": (
                            elt.find(  # type: ignore
                                refloc + "ReferenceLocationAirspace/id"
                            ).text
                            if elt.find(refloc + "ReferenceLocationAirspace")
                            is not None
                            else None
                        ),
                        "aerodrome": (
                            elt.find(  # type: ignore
                                refloc + "ReferenceLocationAerodrome/id"
                            ).text
                            if elt.find(refloc + "ReferenceLocationAerodrome")
                            is not None
                            else None
                        ),
                    },
                    **{
                        "fl_min": (
                            elt.find(  # type: ignore
                                "location/flightLevels/min/level"
                            ).text
                            if elt.find("location/flightLevels/min/level")
                            is not None
                            else 0
                        ),
                        "fl_max": (
                            elt.find(  # type: ignore
                                "location/flightLevels/max/level"
                            ).text
                            if elt.find("location/flightLevels/max/level")
                            is not None
                            else 999
                        ),
                    },
                }
                for elt in self.reply.findall("data/regulations/item")
            ]
        )

        if self.data.empty:
            return

        self.data = self.data.rename(columns=rename_cols)
        self.data = self.data[
            [
                "regulationId",
                "state",
                "type",
                "reason",
                "start",
                "stop",
                "tvId",
                "airspace",
                "aerodrome",
                "fl_min",
                "fl_max",
                "description",
            ]
        ]

        for feat in ["start", "stop"]:
            if feat in self.data.columns:
                self.data = self.data.assign(
                    **{
                        feat: self.data[feat].apply(
                            lambda x: pd.Timestamp(x, tz="utc")
                        )
                    }
                )


class Measures:
    def regulation_list(
        self,
        start: None | timelike = None,
        stop: None | timelike = None,
        traffic_volumes: None | list[str] = None,
        regulations: None | str | list[str] = None,
        fields: None | list[str] = None,
    ) -> None | RegulationList:
        """Returns information about a (set of) given regulation(s).

        :param start: (UTC), by default current time
        :param stop: (UTC), by default one hour later

        :param traffic_volumes: impacted by a given regulation
        :param regulations: identifier(s) related to a regulation


        :param fields: additional fields to request. By default, a set of
            (arguably) relevant fields are requested.

        **Example usage:**

        .. jupyter-execute::

            nm_b2b.regulation_list()

        """

        if start is not None:
            start = to_datetime(start)
        else:
            start = datetime.now(timezone.utc)

        if stop is not None:
            stop = to_datetime(stop)
        else:
            stop = start + timedelta(days=1)

        _tvs = traffic_volumes if traffic_volumes is not None else []
        _fields = fields if fields is not None else []
        if isinstance(regulations, str):
            regulations = [regulations]
        _regulations = regulations if regulations is not None else []

        data = REQUESTS["RegulationListRequest"].format(
            send_time=datetime.now(timezone.utc),
            start=start,
            stop=stop,
            requestedRegulationFields=(
                "<requestedRegulationFields>"
                + "\n".join(
                    f"<item>{field}</item>"
                    for field in default_regulation_fields.union(_fields)
                )
                + "</requestedRegulationFields>"
            ),
            tvs=(
                (
                    "<tvs>"
                    + "\n".join(f"<item>{tv}</item>" for tv in _tvs)
                    + "</tvs>"
                )
                if traffic_volumes is not None
                else ""
            ),
            regulations=(
                (
                    "<regulations>"
                    + "\n".join(
                        f"<item>{regulation}</item>"
                        for regulation in _regulations
                    )
                    + "</regulations>"
                )
                if regulations is not None
                else ""
            ),
        )
        rep = self.post(data)  # type: ignore
        return RegulationList.fromB2BReply(rep)
