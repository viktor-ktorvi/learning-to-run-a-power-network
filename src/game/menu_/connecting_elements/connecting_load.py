import numpy as np

from src.game.menu_.connecting_elements.base import ConnectingElementBase
from src.game.utils import DONT_CLICK_THIS, add_or_overwrite_action, get_busbar_status


# TODO lots of copy pasting from the generator side. Might need to be repeated for the storage elements
class ConnectingLoads(ConnectingElementBase):
    description: str = "Load ID"

    def update_connecting_element_widget(self, *args, **kwargs):
        """
        Get all the loads that connect to the current substation.

        Returns
        -------
        """
        environment = self.game.environment
        loads_at_substation = list(np.arange(environment.n_load)[environment.load_to_subid == self.substation_id])

        # for god-knows-what reason having the option list be [0] screws up the widget
        if loads_at_substation == [0]:
            loads_at_substation = [0, DONT_CLICK_THIS]

        self.connecting_element_widget.options = loads_at_substation
        self.connecting_element_widget.value = loads_at_substation[0]

        self.update_busbar_widget()

    def update_busbar_widget(self, *args, **kwargs):
        """
        Set the busbar status by reading from the action dictionary if it has been set there previously, otherwise by
        reading the current environment observation.

        Returns
        -------
        """
        action_dict = self.game.action_dict
        load_idx = self.connecting_element_widget.value

        if load_idx == DONT_CLICK_THIS:
            raise RuntimeError(
                "Told you not to click it. Could have been a 'Download virus' button for all you knew. It fixes some random bug that doesn't allow just [0] to be an option list."
            )

        self.busbar_widget.options = self.game.get_busbar_options()
        self.busbar_widget.value = get_busbar_status(
            load_idx, action_dict["set_bus"]["loads_id"], self.game.observation.load_bus
        )

        self.update_action_dictionary()

    def update_action_dictionary(self, *args, **kwargs):
        """
        Add the new busbar status to the action dictionary if the busbar in question isn't already there. If it is
        already there, if the action reverts to the original busbar state, then delete the action, otherwise overwrite
        the action.

        Returns
        -------
        """
        load_idx = self.connecting_element_widget.value
        self.game.action_dict["set_bus"]["loads_id"] = add_or_overwrite_action(
            (load_idx, self.busbar_widget.value),
            self.game.action_dict["set_bus"]["loads_id"],
            self.game.observation.load_bus,
        )

        self.print_action_dictionary()
