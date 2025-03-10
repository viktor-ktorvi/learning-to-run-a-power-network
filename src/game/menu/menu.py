import copy
from enum import StrEnum

import ipywidgets
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots
from matplotlib import pyplot as plt

from src.game.game import Game
from src.game.menu.substation.substation import SubstationSubmenu
from src.game.utils import Outputs


class ElementTypes(StrEnum):
    # GENERATOR = "generator"
    # LINE = "line"
    SUBSTATION = "substation"


# TODO docs, comments, cleanup
class Menu(ipywidgets.VBox):
    widget_width: str = "500px"

    outputs = Outputs()

    def __init__(self, game: Game):
        self.game = game

        self.element_type_widget = ipywidgets.ToggleButtons(
            options=list(ElementTypes),
            value=ElementTypes.SUBSTATION,
            description="Element type",
            layout=ipywidgets.Layout(width=self.widget_width),
        )

        # clear action
        clear_action_dict_button = ipywidgets.Button(description="Clear actions")
        self.clear_action_dict()
        clear_action_dict_button.on_click(self.clear_action_dict)

        # try action
        try_action_button = ipywidgets.Button(description="Try action")
        try_action_button.on_click(self.apply_action)
        reset_attempt_button = ipywidgets.Button(description="Reset")

        # reset attempt
        reset_attempt_button.on_click(self.reset_attempt)

        self.element_type_submenu = ipywidgets.VBox()

        # element submenu
        # TODO other potential submenus, e.g., generator, line
        self.substation_submenu = SubstationSubmenu(self.game, self.outputs, self.widget_width)
        self.set_element_type_submenu()
        self.element_type_widget.observe(self.set_element_type_submenu)

        # continue simulation
        continue_simulation_button = ipywidgets.Button(description="Continue simulation")

        self.continue_simulation()
        continue_simulation_button.on_click(self.continue_simulation)

        super().__init__(
            children=[
                clear_action_dict_button,
                try_action_button,
                reset_attempt_button,
                self.element_type_widget,
                self.element_type_submenu,
                continue_simulation_button,
            ]
        )

    def set_element_type_submenu(self, *args):
        if self.element_type_widget.value == ElementTypes.SUBSTATION:
            self.element_type_submenu = self.substation_submenu

    @outputs.action.capture()
    def clear_action_dict(self, *args):
        self.game.clear_action_dict()
        self.outputs.action.clear_output()
        self.game.print_action_dict()

    @outputs.plot.capture()
    def continue_simulation(self, *args):
        self.outputs.plot.clear_output()
        self.outputs.action.clear_output()

        observation = self.game.continue_simulation(self.game.action_dict)
        self.game.plotter.plot_obs(observation)
        plt.gcf().suptitle("Grid with a problematic state")
        show_inline_matplotlib_plots()

        self.print_action_dict()

    @outputs.action.capture()
    def print_action_dict(self):
        self.game.clear_action_dict()
        self.game.print_action_dict()

    @outputs.plot.capture()
    def apply_action(self, *args):
        self.outputs.plot.clear_output()

        action = self.game.environment.action_space(self.game.action_dict)
        observation, reward, _, _ = copy.deepcopy(self.game.environment).step(action)
        self.game.plotter.plot_obs(observation)
        plt.gcf().suptitle("Grid after applying the action")

        print(f"Action reward = {reward}")

        show_inline_matplotlib_plots()

    @outputs.plot.capture()
    def reset_attempt(self, *args):
        self.outputs.plot.clear_output()
        self.outputs.action.clear_output()

        self.game.clear_action_dict()
        self.game.plotter.plot_obs(self.game.observation)
        plt.gcf().suptitle("Grid with a problematic state")
        show_inline_matplotlib_plots()
