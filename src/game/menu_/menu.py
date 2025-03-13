from enum import StrEnum

import ipywidgets
import numpy as np
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots
from matplotlib import pyplot as plt

from src.game.game import Game
from src.game.menu_.connecting_elements.connecting_generator import ConnectingGenerators
from src.game.menu_.connecting_elements.connecting_lines import ConnectingLines
from src.game.menu_.connecting_elements.connecting_load import ConnectingLoads


class ConnectingElementType(StrEnum):
    LINE = "Line"
    GENERATOR = "Generator"
    LOAD = "Load"


class Menu(ipywidgets.VBox):
    widget_width: str = "1000px"
    action_output: ipywidgets.Output = ipywidgets.Output()
    plot_output: ipywidgets.Output = ipywidgets.Output()

    def __init__(self, game: Game):
        self.game = game
        self.connecting_element_submenus = {}

        # SUBSTATION ID
        self.substation_id_widget = ipywidgets.ToggleButtons(
            options=self.game.get_substation_ids(),
            value=self.game.get_substation_ids()[0],
            description="Substation ID",
            layout=ipywidgets.Layout(width=self.widget_width),
        )

        # CONNECTING ELEMENT TYPE
        self.connecting_element_type_widget = ipywidgets.ToggleButtons(
            description="Connecting element type",
            layout=ipywidgets.Layout(width=self.widget_width),
        )

        self.substation_id_widget.observe(self.update_connecting_element_type, names=["value"])

        # CONNECTING ELEMENT
        self.connecting_element_type_widget.observe(self.update_connecting_element_submenu, names=["value"])

        super().__init__(children=(self.substation_id_widget, self.connecting_element_type_widget))

        self.update_connecting_element_type()

        self.continue_simulation()

    @plot_output.capture()
    def continue_simulation(self):
        observation = self.game.continue_simulation(self.game.action_dict)
        self.game.plotter.plot_obs(observation)
        plt.gcf().suptitle("Grid with a problematic state")
        show_inline_matplotlib_plots()

    def update_connecting_element_type(self, *args, **kwargs):
        """
        Update the connecting element type widget options and value depending on the types of elements that are attached
        to the currently selected substation. Initialize the connecting element submenus if not already initialized.

        Parameters
        ----------
        args
        kwargs

        Returns
        -------
        """
        options = []
        substation_id = self.substation_id_widget.value

        if substation_id in np.stack((self.game.environment.line_ex_to_subid, self.game.environment.line_or_to_subid)):
            options.append(ConnectingElementType.LINE)
            if ConnectingElementType.LINE not in self.connecting_element_submenus:
                self.connecting_element_submenus[ConnectingElementType.LINE] = ConnectingLines(
                    substation_id, self.game, self.widget_width, self.action_output
                )

        if substation_id in self.game.environment.gen_to_subid:
            options.append(ConnectingElementType.GENERATOR)
            if ConnectingElementType.GENERATOR not in self.connecting_element_submenus:
                self.connecting_element_submenus[ConnectingElementType.GENERATOR] = ConnectingGenerators(
                    substation_id, self.game, self.widget_width, self.action_output
                )

        if substation_id in self.game.environment.load_to_subid:
            options.append(ConnectingElementType.LOAD)
            if ConnectingElementType.LOAD not in self.connecting_element_submenus:
                self.connecting_element_submenus[ConnectingElementType.LOAD] = ConnectingLoads(
                    substation_id, self.game, self.widget_width, self.action_output
                )

        self.connecting_element_type_widget.options = options
        self.connecting_element_type_widget.value = options[0]
        self.update_connecting_element_submenu()

    def update_connecting_element_submenu(self, *args, **kwargs):
        """
        Update the connecting element submenu. For the chosen connecting element type update its substation ID and its
        connecting elements' widget.

        Parameters
        ----------
        args
        kwargs

        Returns
        -------
        """
        self.children = (
            self.substation_id_widget,
            self.connecting_element_type_widget,
            self.connecting_element_submenus[self.connecting_element_type_widget.value],
        )

        connecting_element_submenu = self.connecting_element_submenus[self.connecting_element_type_widget.value]
        connecting_element_submenu.set_substation_ID(self.substation_id_widget.value)
        connecting_element_submenu.update_connecting_element_widget()
