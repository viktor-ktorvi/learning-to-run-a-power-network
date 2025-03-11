import numpy as np

from src.game.game import Game
from src.game.menu.substation.connecting_element import ConnectingElementSubmenu
from src.game.utils import (
    DONT_CLICK_THIS,
    Outputs,
    add_or_overwrite_action,
    get_busbar_status,
)


class ConnectingGeneratorSubmenu(ConnectingElementSubmenu):
    def __init__(self, game: Game, outputs: Outputs, widget_width: str):
        super().__init__("Connecting generator ID", game, outputs, widget_width)

    def update_connecting_element_widget(self, substation_id: int):
        environment = self.game.environment
        generators_at_substation = list(np.arange(environment.n_gen)[environment.gen_to_subid == substation_id])

        # for god-knows-what reason having the option list be [0] screws up the widget
        if generators_at_substation == [0]:
            generators_at_substation = [0, DONT_CLICK_THIS]

        self.connecting_element_widget.options = generators_at_substation
        self.connecting_element_widget.value = generators_at_substation[0]

    def update_busbar_widget(self, *args):
        action_dict = self.game.action_dict

        generator_idx = self.connecting_element_widget.value

        if generator_idx == DONT_CLICK_THIS:
            raise RuntimeError(
                "Told you not to click it. Could have been a 'Download virus' button for all you knew. It fixes some random bug that doesn't allow just [0] to be an option list."
            )

        self.busbar_widget.options = self.game.get_busbar_options()
        self.busbar_widget.value = get_busbar_status(
            generator_idx, action_dict["set_bus"]["generators_id"], self.game.observation.gen_bus
        )

    def record_busbar_actions(self, *args):
        generator_idx = self.connecting_element_widget.value

        self.game.action_dict["set_bus"]["generators_id"] = add_or_overwrite_action(
            (generator_idx, self.busbar_widget.value),
            self.game.action_dict["set_bus"]["generators_id"],
            self.game.observation.gen_bus,
        )

        # print the actions taken so far
        self.outputs.action.clear_output()
        self.game.print_action_dict()
