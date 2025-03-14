from src.game.menu.connecting_elements.base import ConnectingElementBase
from src.game.utils import add_or_overwrite_action, get_busbar_status, get_line_id


class ConnectingLines(ConnectingElementBase):
    description: str = "Line connecting to substation"

    def update_connecting_element_widget(self, *args, **kwargs):
        """
        Get all the lines that connect to the current substation, either on the OR or EX side.

        Returns
        -------
        """
        environment = self.game.environment

        lines_ex_at_substation = list(environment.line_or_to_subid[environment.line_ex_to_subid == self.substation_id])

        lines_or_at_substation = list(environment.line_ex_to_subid[environment.line_or_to_subid == self.substation_id])

        self.connecting_element_widget.options = lines_ex_at_substation + lines_or_at_substation
        self.connecting_element_widget.value = self.connecting_element_widget.options[0]

        self.update_busbar_widget()

    def update_busbar_widget(self, *args, **kwargs):
        """
        Set the busbar status by reading from the action dictionary if it has been set there previously, otherwise by
        reading the current environment observation.

        Returns
        -------

        Raises
        ------
        ValueError
            If the selected line somehow doesn't exist.
        """
        line_destination = self.connecting_element_widget.value

        action_dict = self.game.action_dict
        observation = self.game.observation
        environment = self.game.environment

        line_or_idx, line_ex_idx = get_line_id(environment, self.substation_id, line_destination)

        if line_or_idx.size == 1:
            self.busbar_widget.value = get_busbar_status(
                line_or_idx.item(), action_dict["set_bus"]["lines_or_id"], observation.line_or_bus
            )

            self.update_action_dictionary()
            return

        if line_ex_idx.size == 1:
            self.busbar_widget.value = get_busbar_status(
                line_ex_idx.item(), action_dict["set_bus"]["lines_ex_id"], observation.line_ex_bus
            )

            self.update_action_dictionary()
            return

        raise ValueError(f"No line was found between substations {self.substation_id} and {line_destination}")

    def update_action_dictionary(self, *args, **kwargs):
        """
        Add the new busbar status to the action dictionary if the busbar in question isn't already there. If it is
        already there, if the action reverts to the original busbar state, then delete the action, otherwise overwrite
        the action.

        Returns
        -------

        Raises
        ------
        ValueError
            If the selected line somehow doesn't exist.
        """
        line_destination = self.connecting_element_widget.value
        line_or_idx, line_ex_idx = get_line_id(self.game.environment, self.substation_id, line_destination)

        observation = self.game.observation
        if line_or_idx.size == 1:
            self.game.action_dict["set_bus"]["lines_or_id"] = add_or_overwrite_action(
                (line_or_idx.item(), self.busbar_widget.value),
                self.game.action_dict["set_bus"]["lines_or_id"],
                observation.line_or_bus,
            )

            self.print_action_dictionary()
            return

        if line_ex_idx.size == 1:
            self.game.action_dict["set_bus"]["lines_ex_id"] = add_or_overwrite_action(
                (line_ex_idx.item(), self.busbar_widget.value),
                self.game.action_dict["set_bus"]["lines_ex_id"],
                observation.line_ex_bus,
            )

            self.print_action_dictionary()
            return

        raise ValueError(f"No line was found between substations {self.substation_id} and {line_destination}")
