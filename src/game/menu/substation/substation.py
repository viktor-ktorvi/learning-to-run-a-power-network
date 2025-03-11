from enum import StrEnum

import ipywidgets

from src.game.game import Game
from src.game.menu.substation.connecting_generator import ConnectingGeneratorSubmenu
from src.game.menu.substation.connecting_line import ConnectingLineSubmenu
from src.game.utils import Outputs

# TODO loads and generators
#  "generators_id": [(gen_id, new_bus), (gen_id, new_bus), ...],
#  "storages_id": [(storage_id, new_bus), (storage_id, new_bus), ...]

# TODO togglebutton + vbox for connecting element: line, generator, load
#  ConnectingLineSubsubmenu, ConnectingGeneratorSubsubmenu, ConnectingLoadSubsubmenu


class ConnectingElementTypes(StrEnum):
    LINES = "lines"
    GENERATORS = "generators"


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
            value=list(ConnectingElementTypes)[0],
            description="Connecting element type",
            layout=ipywidgets.Layout(width=widget_width),
        )

        self.connecting_element_submenus = {
            ConnectingElementTypes.LINES: ConnectingLineSubmenu(game, outputs, widget_width),
            ConnectingElementTypes.GENERATORS: ConnectingGeneratorSubmenu(game, outputs, widget_width),
        }

        # connecting element submenu
        self.connecting_element_submenu = ipywidgets.VBox()
        self.set_connecting_element_submenu()
        self.connecting_element_type_widget.observe(self.set_connecting_element_submenu, names=["value"])
        self.connecting_element_type_widget.observe(self.update_connecting_element_widget, names=["value"])

        # ORCHESTRATING THE CALLBACKS

        # connecting line callbacks
        self.update_connecting_element_widget()
        self.substation_ids_widget.observe(self.update_connecting_element_widget, names=["value"])

        self.update_connecting_element_busbar_widget()
        for submenu in self.connecting_element_submenus.values():
            submenu.connecting_element_widget.observe(self.update_connecting_element_busbar_widget, names=["value"])

            submenu.busbar_widget.observe(self.record_connecting_element_busbar_actions, names=["value"])

        super().__init__(
            children=(self.substation_ids_widget, self.connecting_element_type_widget, self.connecting_element_submenu)
        )

    def set_connecting_element_submenu(self, *args):
        self.connecting_element_submenu = self.connecting_element_submenus[self.connecting_element_type_widget.value]
        self.children = (
            self.substation_ids_widget,
            self.connecting_element_type_widget,
            self.connecting_element_submenu,
        )

    def update_connecting_element_widget(self, *args):
        @self.outputs.action.capture()
        def callback():
            self.connecting_element_submenus[
                self.connecting_element_type_widget.value
            ].update_connecting_element_widget(self.substation_ids_widget.value)

        callback()

    def update_connecting_element_busbar_widget(self, *args):
        @self.outputs.action.capture()
        def callback():
            self.connecting_element_submenus[self.connecting_element_type_widget.value].update_busbar_widget(
                self.substation_ids_widget.value
            )

        callback()

    def record_connecting_element_busbar_actions(self, *args):
        @self.outputs.action.capture()
        def callback():
            self.connecting_element_submenus[self.connecting_element_type_widget.value].record_busbar_actions(
                self.substation_ids_widget.value
            )

        callback()
