from enum import StrEnum

import ipywidgets

from src.game.game import Game
from src.game.menu.substation.connecting_line import ConnectingLineSubmenu
from src.game.utils import Outputs

# TODO loads and generators
#  "generators_id": [(gen_id, new_bus), (gen_id, new_bus), ...],
#  "storages_id": [(storage_id, new_bus), (storage_id, new_bus), ...]

# TODO togglebutton + vbox for connecting element: line, generator, load
#  ConnectingLineSubsubmenu, ConnectingGeneratorSubsubmenu, ConnectingLoadSubsubmenu


class ConnectingElementTypes(StrEnum):
    LINES = "lines"


class SubstationSubmenu(ipywidgets.VBox):
    outputs: Outputs

    def __init__(self, game: Game, outputs: Outputs, widget_width: str):
        self.game = game
        self.outputs = outputs

        substation_ids = game.get_substation_ids()
        self.substation_ids_widget = ipywidgets.ToggleButtons(
            options=substation_ids,
            value=substation_ids[0],
            description="Substation ID",
            layout=ipywidgets.Layout(width=widget_width),
        )

        self.connecting_element_type_widget = ipywidgets.ToggleButtons(
            options=list(ConnectingElementTypes),
            value=ConnectingElementTypes.LINES,
            description="Connecting element type",
            layout=ipywidgets.Layout(width=widget_width),
        )

        self.connecting_lines_submenu = ConnectingLineSubmenu(game, outputs, widget_width)

        # connecting element submenu
        self.connecting_element_submenu = ipywidgets.VBox()
        self.set_connecting_element_submenu()
        self.connecting_element_type_widget.observe(self.set_connecting_element_submenu)

        # connecting line callbacks
        self.update_connecting_line_widget()
        self.substation_ids_widget.observe(self.update_connecting_line_widget, names=["value"])

        self.update_connecting_line_busbar_widget()
        self.connecting_lines_submenu.connecting_line_widget.observe(
            self.update_connecting_line_busbar_widget, names=["value"]
        )
        # self.substation_ids_widget.observe(self.update_connecting_line_busbar_widget, names=["value"])

        self.connecting_lines_submenu.busbar_widget.observe(self.record_connecting_line_busbar_actions)

        super().__init__(
            children=(self.substation_ids_widget, self.connecting_element_type_widget, self.connecting_element_submenu)
        )

    def set_connecting_element_submenu(self):
        if self.connecting_element_type_widget.value == ConnectingElementTypes.LINES:
            self.connecting_element_submenu = self.connecting_lines_submenu

    def update_connecting_line_widget(self, *args):
        @self.outputs.action.capture()
        def callback():
            self.connecting_lines_submenu.update_connecting_line_widget(self.substation_ids_widget.value)

        callback()

    def update_connecting_line_busbar_widget(self, *args):
        @self.outputs.action.capture()
        def callback():
            self.connecting_lines_submenu.update_busbar_widget(self.substation_ids_widget.value)

        callback()

    def record_connecting_line_busbar_actions(self, *args):
        @self.outputs.action.capture()
        def callback():
            self.connecting_lines_submenu.record_busbar_actions(self.substation_ids_widget.value)

        callback()
