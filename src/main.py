# pylint: disable=unspecified-encoding

import os
import re
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Dict
import tabulate

from config import LANGUAGE, STRINGS
from data_classes import Eta, RouteInfo, Interchange
from route_data import InterchangeLoader, RouteLoader


def ask_interchange_path() -> str:
    """Get all JSON files in ./interchanges, then ask the user to select one"""
    file_paths = [
        f"../interchanges/{filename}"
        for filename in os.listdir("../interchanges/")
        if os.path.isfile(f"../interchanges/{filename}")\
        and filename.endswith(".json")\
        and not filename.endswith("_CACHE.json")\
        and not filename.endswith("TEMPLATE.json")
    ]

    table = tabulate.tabulate(
        [[i, j.replace("../interchanges/", "", 1)] for i, j in enumerate(file_paths)],
        headers=["No.", "Filename"],
        tablefmt="double_outline"
    )
    print(table)
    print(
        "\n"
        "Please select an entry from above. Type the corresponding number and press enter, "
        "or enter q to quit."
        "\n"
        "Note: These files come from the /interchanges/ folder."
        "\n"
    )
    user_input = ""
    while True:
        user_input = input("ENTRY: ")
        try:
            assert 0 <= int(user_input) < len(file_paths)
            break
        except (ValueError, AssertionError):
            pass

        if user_input.lower().startswith("q"):
            exit()

    return file_paths[int(user_input)]


def stop_position_sort_key(routes: RouteInfo):
    """The sort key used to sort an iterable of RouteInfo() objects by stop position."""
    route_pos = routes.stop_position
    letters = re.findall(r"[A-Za-z]+", route_pos)
    if not letters:
        letters = [""]

    digits = re.findall(r"\d+", route_pos)
    if not digits:
        digits = [-1]

    return (letters[0], int(digits[0]))


class App(tk.Tk):
    TREEVIEW_COLUMNS = [
        "route",
        "stop_sequence",
        "stop_position",
        f"dest_{LANGUAGE}",
        "company",
        "eta",
    ]

    TREEVIEW_COL_MINWIDTHS = {
        "route": 50,
        "stop_sequence": 20,
        "stop_position": 20,
        f"dest_{LANGUAGE}": 20,
        "company": 20,
        "eta": 200,
    }

    TREEVIEW_COL_DEFAULT_WIDTHS = {
        "route": 50,
        "stop_sequence": 60,
        "stop_position": 60,
        f"dest_{LANGUAGE}": 200,
        "company": 60,
        "eta": 200,
    }


    SORT_KEYS = {
        "route": lambda x: int(re.findall(r"\d+", x.route)[0]), # Sort by integer part of route
        "stop_sequence": lambda x: x.stop_sequence,
        "stop_position": stop_position_sort_key, # Sort by letter part, then by integer part
        f"dest_{LANGUAGE}": lambda x: x.__dict__[f"dest_{LANGUAGE}"],
        "company": lambda x: x.company,
        "eta": lambda x: x.eta[0] if x.eta else Eta(eta=datetime(9999, 12, 31, 23, 59, 59), company="JOINT", remark=""), # Sort by first ETA, if no ETA then just put at last
    }


    def __init__(self) -> None:
        super().__init__()
        ttk.Style(self).theme_use("clam")

        self.resizable(True, True)
        self.minsize(600, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        print("Loading started. Please do not terminate the program.", datetime.now())
        self.interchanges = InterchangeLoader(f"{INTERCHANGE_PATH}").data
        self.route_loader = RouteLoader(self.interchanges, filename=INTERCHANGE_PATH.replace(".json", "_CACHE.json", 1))
        print("Loading finished.", datetime.now())

        self._init_notebook()
        self.mainloop()


    def _init_notebook(self):
        """Initialize a notebook, put a tab frame for every interchange, then put a treeview in each tab"""
        self.notebook = ttk.Notebook(self)
        self.notebook.grid_propagate(False)
        self.notebook.grid(row=0, column=0, sticky="NESW")

        self.tab_frames: Dict[str, tk.Frame] = {}
        self.treeviews: Dict[str, ttk.Treeview] = {}

        for interchange in self.interchanges:
            # Tab
            frame = tk.Frame(self.notebook)
            self.notebook.add(frame, text=getattr(interchange, f"name_{LANGUAGE}"))

            frame.grid_propagate(False)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)

            # Treeview
            treeview = ttk.Treeview(
                frame,
                columns=self.TREEVIEW_COLUMNS,
                selectmode="browse",
                show="headings",
            )

            # Set column headers, make them trigger the sort method when clicked, and set their width
            for column in self.TREEVIEW_COLUMNS:
                treeview.heading(
                    column,
                    text=STRINGS[f"TREEVIEW_{column.upper()}"],
                    command=lambda _intcode=interchange.interchange_code, _col=column, _tv=treeview:\
                        self.sort_and_add_routes(_intcode, _col, _tv),
                )

                treeview.column(
                    column,
                    minwidth=self.TREEVIEW_COL_MINWIDTHS[column],
                    width=self.TREEVIEW_COL_DEFAULT_WIDTHS[column],
                    stretch=bool(column == "eta"),
                )

            # Adding all routes
            self.sort_and_add_routes(interchange.interchange_code, "route", treeview)

            # Button
            update_button = tk.Button(
                frame,
                text=STRINGS["BUTTON_UPDATE_ETA"],
                command=lambda _int=interchange: self.handle_update_button(_int)
            )

            # Grid
            treeview.grid(row=0, column=0, sticky="NESW")
            update_button.grid(row=1, column=0, sticky="W")

            # Store tab and treeview to global variables for later usage
            self.tab_frames[interchange.interchange_code] = frame
            self.treeviews[interchange.interchange_code] = treeview


    def sort_and_add_routes(self, interchange_code: str, column: str, treeview: ttk.Treeview):
        # Delete all items
        treeview.delete(*treeview.get_children())

        routes = sorted(self.route_loader.routes[interchange_code], key=self.SORT_KEYS[column])

        for route in routes:
            treeview.insert(
                "",
                tk.END,
                iid=f"{route.route}_{route.bound}",
                values=[route.__dict__[x] for x in self.TREEVIEW_COLUMNS]
            )


    def handle_update_button(self, interchange: Interchange):
        self.route_loader.update_all_eta(interchange)
        for route in self.route_loader.routes[interchange.interchange_code]:
            self.treeviews[interchange.interchange_code].set(
                f"{route.route}_{route.bound}",
                "eta",
                " || ".join([str(eta) for eta in route.eta]) if route.eta else STRINGS["NO_DEPARTURE"]
            )


INTERCHANGE_PATH = ask_interchange_path()
App()
