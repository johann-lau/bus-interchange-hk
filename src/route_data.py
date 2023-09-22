# pylint: disable=unspecified-encoding

import json
from datetime import datetime
from threading import Thread
from typing import Any, Dict, List, Literal

import requests

from data_classes import MyEncoder, Stop, Eta, Interchange, RouteInfo, InterchangeRoutes, SerializedInterchangeList
from config import LANGUAGE, CTB_LANGUAGE, KMB_ENDPOINT, CTB_ENDPOINT, CTB_BATCH_ROUTE_ENDPOINT, CTB_BATCH_ETA_ENDPOINT, REQUEST_TIMEOUT_SECS


class InterchangeLoader:
    """A class to get data from the json file (usually interchanges.json) and return a Interchanges Dict"""

    data: List[Interchange] = []

    def __init__(self, filename: str) -> None:
        self.data = self._load_json_routes(filename)

    def _load_json_routes(self, filename: str) -> List[Interchange]:
        # Get data from JSON directly
        with open(filename) as f:
            raw_data: SerializedInterchangeList = json.load(f)

        # Deserialize stops into a list of Interchange() objects
        data: List[Interchange] = [
            Interchange(
                interchange_id = interchange_id,
                name_en = interchange_data["name_en"], # type: ignore
                name_sc = interchange_data["name_sc"], # type: ignore
                name_tc = interchange_data["name_tc"], # type: ignore
                stops_kmb = [
                    Stop(stop_posiiton = stop_position, stop_id = stop_id)
                    for stop_position, stop_id in interchange_data["stops"]["KMB"] # type: ignore
                ],

                stops_ctb = [
                    Stop(stop_posiiton = stop_position, stop_id = stop_id)
                    for stop_position, stop_id in interchange_data["stops"]["CTB"] # type: ignore
                ]
            )
            for interchange_id, interchange_data in raw_data.items()
        ]


        # Return deserialized data
        return data


class RouteLoader:
    """A class to load all routes of the interchange(s) for all companies"""
    filename: str
    interchanges: List[Interchange]
    routes: InterchangeRoutes

    def __init__(self, interchanges: List[Interchange], filename: str) -> None:
        self.filename = filename
        self.interchanges = interchanges
        self.routes = self._fetch_all_routes()

    def _fetch_all_routes(self) -> InterchangeRoutes:
        """Get all routes passing through all the interchanges"""
        # Try to import from JSON file, fallbacks to regular API calling if needed
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
            # Serialize
            return {
                interchange_code: [
                    RouteInfo(**route_info, eta = [])
                    for route_info in routes
                ]
                for interchange_code, routes in data.items()
            }
        except FileNotFoundError:
            pass

        raw_routes: InterchangeRoutes = {}
        threads: List[Thread] = []

        # All KMB routes ever
        kmb_all_route_stops = requests.get(f"{KMB_ENDPOINT}/route-stop", timeout=REQUEST_TIMEOUT_SECS).json()["data"]

        # For every interchange, start threds to append route data
        for interchange in self.interchanges:
            raw_routes[interchange.interchange_code] = []

            # KMB
            # For every stop, get all routes
            for stop in interchange.stops_kmb:
                # Filter the route-stops that have the same stop as the current iteration's stop
                routes = filter(lambda x: x["stop"]  == stop.stop_id, kmb_all_route_stops)

                # For every route, start a thread to append a RouteInfo object
                # Also, don't add the same routes with the same bound - they won't be handled separately by the ETA API anyways
                added_routes = []
                for route in routes:
                    if (route["route"], route["bound"]) in added_routes:
                        continue
                    added_routes.append((route["route"], route["bound"]))


                    t = Thread(
                        target = lambda: raw_routes[interchange.interchange_code].append(
                                self._fetch_kmb_route_info(
                                    stop_sequence = route["seq"],
                                    stop_position = stop.stop_position,
                                    route = route["route"],
                                    bound = route["bound"],
                                    service_type = route["service_type"]
                                )
                            ),
                        daemon = True)
                    t.start()
                    threads.append(t)


            # CTB
            # For every stop, get all routes
            for stop in interchange.stops_ctb:
                routes = requests.get(f"{CTB_BATCH_ROUTE_ENDPOINT}/stop-route/CTB/{stop.stop_id}", timeout=REQUEST_TIMEOUT_SECS).json()['data']
                for route in routes:
                    # For every route, start a thread to append a RouteInfo object
                    t = Thread(target = lambda: raw_routes[interchange.interchange_code].append(
                            self._fetch_ctb_route_info(
                                stop_sequence = route["seq"],
                                stop_position = stop.stop_position,
                                route = route["route"],
                                bound = route["dir"],
                            )
                        ),
                        daemon = True)
                    t.start()
                    threads.append(t)

        # Wait for all threads to terminate before further processing
        for thread in threads:
            thread.join()

        # Remove None's and merge routes, then sort the list
        for interchange in self.interchanges:
            interchange_routes = raw_routes[interchange.interchange_code]

            # Remove None from the list, which arises from non-existent CTB routes
            interchange_routes = list(filter(lambda x: x, interchange_routes))

            # Merge routes of the same company
            interchange_routes = self._merge_routes(interchange_routes)

            # Sort the routes
            interchange_routes = sorted(interchange_routes, key=lambda x: x.stop_position)

            # Finally, put the merged routes to the output
            raw_routes[interchange.interchange_code] = interchange_routes

        # Store output to file
        with open(self.filename, "x") as f:
            json.dump(
                raw_routes,
                f,
                ensure_ascii=False,
                indent=4,
                cls=MyEncoder
            )

        return raw_routes


    def _fetch_kmb_route_info(self, stop_sequence: int, stop_position: str, route: str, bound: Literal["I", "O"], service_type: str) -> RouteInfo:
        bound_str = "inbound" if bound == "I" else "outbound"
        raw_info = requests.get(f"{KMB_ENDPOINT}/route/{route}/{bound_str}/{service_type}", timeout=REQUEST_TIMEOUT_SECS).json()['data']

        info = RouteInfo(
            route = raw_info["route"],
            stop_sequence = int(stop_sequence),
            stop_position = stop_position,
            bound = bound,
            dest_en = raw_info["dest_en"],
            dest_tc = raw_info["dest_tc"],
            dest_sc = raw_info["dest_sc"],
            company = "KMB",
            eta = [],
        )

        return info


    def _fetch_ctb_route_info(self, stop_sequence: int, stop_position: str, route: str, bound: Literal["I", "O"]) -> RouteInfo:
        raw_info = requests.get(f"{CTB_ENDPOINT}/route/CTB/{route}", timeout=REQUEST_TIMEOUT_SECS).json()['data']

        if not raw_info:
            raise ValueError("Invalid parameter for _fetch_ctb_route_info")

        dest_str = "dest" if bound == "O" else "orig"

        info = RouteInfo(
            route = raw_info['route'],
            stop_sequence = int(stop_sequence),
            stop_position = stop_position,
            bound = bound,
            dest_en = raw_info[f"{dest_str}_en"],
            dest_tc = raw_info[f"{dest_str}_tc"],
            dest_sc = raw_info[f"{dest_str}_sc"],
            company = "CTB",
            eta = [],
        )

        return info


    def _merge_routes(self, input_routes: List[RouteInfo]):
        output_routes = []
        added_routes = []

        for i, route in enumerate(input_routes):
            # If this route has already been added, skip this
            if (route.route, route.stop_sequence) in added_routes:
                continue
            added_routes.append((route.route, route.stop_sequence))

            # Find repeated routes with same stop sequence that appear later than the current item
            # The "same stop sequence" condition is used to allow adding the same route twice in case there are two directions,
            # Which would happen for bus terminus
            repeats = list(filter(lambda x: x.route == route.route and x.stop_sequence == route.stop_sequence, input_routes[i+1:]))

            if repeats:
                # Copy the same RouteInfo(), with two items to note:
                # 1. Use the company "JOINT"
                # 2. Use KMB's stop position. Because this always appear first, `route` must be the KMB data while `repeats` must have the CTB data
                # 3. Use CTB's bound
                new_route = RouteInfo(
                    route = route.route,
                    stop_sequence = route.stop_sequence,
                    stop_position = route.stop_position, # This should always come from KMB
                    bound = repeats[0].bound,
                    dest_en = route.dest_en,
                    dest_tc = route.dest_tc,
                    dest_sc = route.dest_sc,
                    company = "JOINT",
                    eta = []
                )
            elif route.route in ["104", "982X"]:
                new_route = route
                added_routes.append((route.route, route.stop_sequence - 2))
                added_routes.append((route.route, route.stop_sequence - 1))
                added_routes.append((route.route, route.stop_sequence + 1))
                added_routes.append((route.route, route.stop_sequence + 2))
            else:
                new_route = route
            output_routes.append(new_route)

        return output_routes


    def update_all_eta(self, interchange: Interchange) -> None:
        interchange_routes = self.routes[interchange.interchange_code]

        # KMB Batch APIs
        kmb_stop_ids = [x.stop_id for x in interchange.stops_kmb]
        kmb_etas: List[Dict[str, Any]] = []

        for stop_id in kmb_stop_ids:
            kmb_etas.extend(requests.get(f"{KMB_ENDPOINT}/stop-eta/{stop_id}", timeout=REQUEST_TIMEOUT_SECS).json()["data"])

        # CTB Batch APIs
        ctb_stop_ids = [x.stop_id for x in interchange.stops_ctb]
        ctb_etas: List[Dict[str, Any]] = []

        for stop_id in ctb_stop_ids:
            ctb_etas.extend(requests.get(f"{CTB_BATCH_ETA_ENDPOINT}/stop-eta/CTB/{stop_id}?lang={CTB_LANGUAGE}", timeout=REQUEST_TIMEOUT_SECS).json()["data"])

        for route in interchange_routes:
            kmb_match_etas = filter(lambda eta: eta["route"] == route.route and eta["dir"] == route.bound, kmb_etas)
            ctb_match_etas = filter(lambda eta: eta["route"] == route.route and eta["dir"] == route.bound, ctb_etas)
            match_etas = list(kmb_match_etas) + list(ctb_match_etas)
            route.eta = [
                Eta(
                    eta = datetime.fromisoformat(eta["eta"]),
                    company = eta["co"],
                    remark = eta["rmk"] if eta["co"] == "CTB" else eta[f"rmk_{LANGUAGE}"],
                    include_company = bool(route.company == "JOINT")
                )
                for eta in match_etas
                if eta["eta"]
            ]

        self.routes[interchange.interchange_code] = interchange_routes
