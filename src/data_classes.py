"""Data classes Stop, Eta, Interchange and RouteInfo,
as well as MyEncoder to serialize these data classes to JSON."""
from __future__ import annotations

from datetime import datetime
from functools import total_ordering
from json import JSONEncoder
from typing import Dict, List, Literal, Union

from config import STRINGS


class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, RouteInfo):
            return {k: v for k, v in o.__dict__.items() if k != "eta"}
        return o.__dict__


# Custom data classes
class Stop:
    stop_position: str
    stop_id: str

    def __init__(self, *, stop_posiiton: str, stop_id: str) -> None:
        self.stop_position = stop_posiiton
        self.stop_id = stop_id

    def __repr__(self) -> str:
        return (
            f"Stop(stop_position='{self.stop_position}', "
            f"stop_id={self.stop_id})")


@total_ordering
class Eta:
    """Stores one ETA of a route"""
    eta: datetime
    company: str
    remark: str
    include_company: bool = False

    def __init__(self, eta: datetime, company: str, remark: str, include_company: bool = False) -> None:
        self.eta = eta
        self.company = company
        self.remark = remark
        self.include_company = include_company

    def __eq__(self, other_eta: Eta) -> bool:
        return self.eta == other_eta.eta
    
    def __lt__(self, other_eta: Eta) -> bool:
        return self.eta < other_eta.eta

    def __str__(self) -> str:
        out = self.eta.strftime("%H:%M:%S")
        if self.include_company:
            out += f" [{STRINGS[self.company + '_SHORT']}]"
        if self.remark:
            out += f" [{STRINGS['REMARK']}{self.remark}]"

        return out

    def __repr__(self) -> str:
        return self.__str__()


class Interchange:
    interchange_code: str # User-defined code found in JSON file
    name_en: str
    name_sc: str
    name_tc: str
    stops_kmb: List[Stop]
    stops_ctb: List[Stop]

    def __init__(self, *, interchange_id: str, name_en: str, name_sc: str, name_tc: str, stops_kmb: List[Stop], stops_ctb: List[Stop]) -> None:
        self.interchange_code = interchange_id
        self.name_en: str = name_en
        self.name_sc: str = name_sc
        self.name_tc: str = name_tc
        self.stops_kmb: List[Stop] = stops_kmb
        self.stops_ctb: List[Stop] = stops_ctb
    
    def __repr__(self) -> str:
        return (
            f"Interchange(interchange_code='{self.interchange_code}', "
            f"name_en={self.name_en}, "
            f"name_tc='{self.name_tc}', "
            f"name_sc='{self.name_sc}', "
            f"stops_kmb='{self.stops_kmb}'"
            f"stops_ctb='{self.stops_ctb}')")


class RouteInfo:
    route: str
    stop_sequence : int
    stop_position : str
    bound: Literal["I", "O"]
    dest_en: str
    dest_tc: str
    dest_sc: str
    company: str
    eta: List[Eta]

    def __init__(self, *,
                 route: str,
                 stop_sequence: int,
                 stop_position: str,
                 bound: Literal["I", "O"],
                 dest_en: str,
                 dest_tc: str,
                 dest_sc: str,
                 company: str,
                 eta: List[Eta]
                ) -> None:
        self.route = route
        self.stop_sequence = stop_sequence
        self.stop_position = stop_position
        self.bound = bound
        self.dest_en = dest_en
        self.dest_tc = dest_tc
        self.dest_sc = dest_sc
        self.company = company
        self.eta = eta

    def __repr__(self) -> str:
        return (
            f"RouteInfo(route='{self.route}', "
            f"stop_sequence={self.stop_sequence}, "
            f"stop_position='{self.stop_position}', "
            f"dest_en='{self.dest_en}', "
            f"dest_tc='{self.dest_tc}', "
            f"dest_sc='{self.dest_sc}', "
            f"company='{self.company}')"
            f"eta='{self.eta}', ")

    def __str__(self) -> str:
        return self.__repr__()


# Type hints
InterchangeCode = str
SerializedInterchangeList = Dict[InterchangeCode, Dict[str, Union[str, List]]]
InterchangeRoutes = Dict[InterchangeCode, List[RouteInfo]]
