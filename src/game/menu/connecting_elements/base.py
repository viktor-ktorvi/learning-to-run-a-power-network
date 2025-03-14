import ipywidgets

from src.game.game import Game


class ConnectingElementBase(ipywidgets.VBox):
    description: str = "Description"
    substation_id: int = None

    def __init__(self, init_substation_id: int, game: Game, widget_width: str, action_output: ipywidgets.Output):
        self.set_substation_ID(init_substation_id)
        self.game = game
        self.action_output = action_output

        self.connecting_element_widget = ipywidgets.ToggleButtons(
            description=self.description, layout=ipywidgets.Layout(width=widget_width)
        )
        # self.update_busbar_widget()
        self.connecting_element_widget.observe(self.update_busbar_widget, names=["value"])

        self.busbar_widget = ipywidgets.ToggleButtons(
            description="Busbar", options=self.game.get_busbar_options(), layout=ipywidgets.Layout(width=widget_width)
        )
        # self.update_action_dictionary()
        self.busbar_widget.observe(self.update_action_dictionary, names=["value"])

        super().__init__(children=(self.connecting_element_widget, self.busbar_widget))

    def set_substation_ID(self, substation_id: int):
        """
        Set the substation ID.

        Parameters
        ----------
        substation_id: int
            Substation ID.

        Returns
        -------
        """
        self.substation_id = substation_id

    def print_action_dictionary(self):
        """
        Print the action dictionary and output it to the action output.

        Returns
        -------
        """

        @self.action_output.capture()
        def print_action_dict():
            self.game.print_action_dict()

        self.action_output.clear_output()
        print_action_dict()

    def update_connecting_element_widget(self, *args, **kwargs):
        raise NotImplementedError()

    def update_busbar_widget(self, *args, **kwargs):
        raise NotImplementedError()

    def update_action_dictionary(self, *args, **kwargs):
        raise NotImplementedError()
