import ipywidgets

from src.game.game import Game
from src.game.utils import (
    Outputs,
    add_or_overwrite_action,
    get_busbar_status,
    get_line_id,
)


# TODO docs
class ConnectingLineSubmenu(ipywidgets.VBox):
    def __init__(self, game: Game, outputs: Outputs, widget_width: str):
        self.game = game
        self.outputs = outputs

        self.connecting_line_widget = ipywidgets.ToggleButtons(
            description="Connecting line", layout=ipywidgets.Layout(width=widget_width)
        )

        self.busbar_widget = ipywidgets.ToggleButtons(
            description="Busbar",
            options=self.game.get_busbar_options(),
            layout=ipywidgets.Layout(width=widget_width),
        )

        super().__init__(children=(self.connecting_line_widget, self.busbar_widget))

    def update_connecting_line_widget(self, substation_id: int):
        environment = self.game.environment

        lines_ex_at_substation = list(environment.line_or_to_subid[environment.line_ex_to_subid == substation_id])

        lines_or_at_substation = list(environment.line_ex_to_subid[environment.line_or_to_subid == substation_id])

        self.connecting_line_widget.options = lines_ex_at_substation + lines_or_at_substation
        self.connecting_line_widget.value = self.connecting_line_widget.options[0]

    def update_busbar_widget(self, substation_id: int):
        line_destination = self.connecting_line_widget.value

        action_dict = self.game.action_dict
        observation = self.game.observation
        environment = self.game.environment

        line_or_idx, line_ex_idx = get_line_id(environment, substation_id, line_destination)

        if line_or_idx.size == 1:
            busbar_status = get_busbar_status(
                line_or_idx.item(), action_dict["set_bus"]["lines_or_id"], observation.line_or_bus
            )

        elif line_ex_idx.size == 1:
            busbar_status = get_busbar_status(
                line_ex_idx.item(), action_dict["set_bus"]["lines_ex_id"], observation.line_ex_bus
            )

        else:
            raise ValueError(f"No line was found between substations {substation_id} and {line_destination}")

        self.busbar_widget.value = busbar_status

    def record_busbar_actions(self, substation_id: int):
        line_destination = self.connecting_line_widget.value
        line_or_idx, line_ex_idx = get_line_id(self.game.environment, substation_id, line_destination)

        observation = self.game.observation
        if line_or_idx.size == 1:
            self.game.action_dict["set_bus"]["lines_or_id"] = add_or_overwrite_action(
                (line_or_idx.item(), self.busbar_widget.value),
                self.game.action_dict["set_bus"]["lines_or_id"],
                observation.line_or_bus,
            )

        elif line_ex_idx.size == 1:
            self.game.action_dict["set_bus"]["lines_ex_id"] = add_or_overwrite_action(
                (line_ex_idx.item(), self.busbar_widget.value),
                self.game.action_dict["set_bus"]["lines_ex_id"],
                observation.line_ex_bus,
            )

        else:
            raise ValueError(f"No line was found between substations {substation_id} and {line_destination}")

        # print the actions taken so far
        self.outputs.action.clear_output()
        self.game.print_action_dict()
