import copy
from enum import StrEnum

import ipywidgets
import numpy as np
from grid2op import Observation
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

    def __init__(self, game: Game, continue_simulation: bool = True):
        super().__init__()
        self.game = game
        self.connecting_element_submenus = {}

        # APPLY ACTION
        self.apply_action_button = ipywidgets.Button(description="Apply action")
        self.apply_action_button.on_click(self.apply_action)

        # RESET
        self.reset_button = ipywidgets.Button(description="Reset")
        self.reset_button.on_click(self.reset)

        # CONTINUE SIMULATION
        self.continue_simulation_button = ipywidgets.Button(description="Continue simulation")
        self.continue_simulation_button.on_click(self.continue_simulation)

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

        self.update_connecting_element_type()

        if continue_simulation:
            self.continue_simulation()

    def set_children(self):
        """
        Set the children widgets of the VBox.

        Returns
        -------
        """
        self.children = (
            self.apply_action_button,
            self.reset_button,
            self.continue_simulation_button,
            self.substation_id_widget,
            self.connecting_element_type_widget,
            self.connecting_element_submenus[self.connecting_element_type_widget.value],
        )

    @plot_output.capture(clear_output=True)
    def apply_action(self, *args, **kwargs):
        """
        Apply an action to a copy of the environment, step once into the future, and visualize the results.

        Parameters
        ----------
        args
        kwargs

        Returns
        -------
        """
        action = self.game.environment.action_space(self.game.action_dict)
        observation, reward, done, info = copy.deepcopy(self.game.environment).step(action)
        self.plot_grid_state(observation, "Grid after applying the action")

        self.game.print_info()

    def reset(self, *args, **kwargs):
        """
        Reset the menu state to the current state of the grid.

        Parameters
        ----------
        args
        kwargs

        Returns
        -------
        """

        @self.plot_output.capture(clear_output=True)
        def reset_menu():
            self.game.clear_action_dict()
            self.__init__(self.game, continue_simulation=False)
            self.plot_grid_state(self.game.observation, "Grid with a problematic state")

            self.game.print_info()

        reset_menu()

        @self.action_output.capture(clear_output=True)
        def print_action_dict():
            self.game.print_action_dict()

        print_action_dict()

    def plot_grid_state(self, observation: Observation, title: str):
        """
        Plot the grid state for the given observation.

        Parameters
        ----------
        observation: Observation
            Observation.
        title: str
            Title.

        Returns
        -------
        """
        self.game.plotter.plot_obs(observation)
        plt.gcf().suptitle(title)
        show_inline_matplotlib_plots()

    def continue_simulation(self, *args, **kwargs):
        """
        Take the current action dictionary state, apply it to the environment, and continue the simulation.

        Parameters
        ----------
        args
        kwargs

        Returns
        -------
        """

        @self.plot_output.capture(clear_output=True)
        def continue_sim():
            observation, reward, done, info = self.game.continue_simulation(self.game.action_dict)
            self.game.clear_action_dict()
            self.plot_grid_state(observation, "Grid with a problematic state")
            self.game.print_info()

            show_inline_matplotlib_plots()

        continue_sim()

        @self.action_output.capture(clear_output=True)
        def print_action_dictionary():
            self.game.print_action_dict()

        print_action_dictionary()

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
        self.set_children()

        connecting_element_submenu = self.connecting_element_submenus[self.connecting_element_type_widget.value]
        connecting_element_submenu.set_substation_ID(self.substation_id_widget.value)
        connecting_element_submenu.update_connecting_element_widget()
