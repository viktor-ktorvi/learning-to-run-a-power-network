import ipywidgets

from src.game.game import Game
from src.game.utils import Outputs


# TODO docs
class ConnectingElementSubmenu(ipywidgets.VBox):
    def __init__(self, connecting_element_widget_description: str, game: Game, outputs: Outputs, widget_width: str):
        self.game = game
        self.outputs = outputs

        self.connecting_element_widget = ipywidgets.ToggleButtons(
            description=connecting_element_widget_description, layout=ipywidgets.Layout(width=widget_width)
        )

        self.busbar_widget = ipywidgets.ToggleButtons(
            description="Busbar",
            options=self.game.get_busbar_options(),
            layout=ipywidgets.Layout(width=widget_width),
        )

        super().__init__(children=(self.connecting_element_widget, self.busbar_widget))

    def update_connecting_element_widget(self, substation_id: int):
        raise NotImplementedError()

    def update_busbar_widget(self, substation_id: int):
        raise NotImplementedError()

    def record_busbar_actions(self, substation_id: int):
        raise NotImplementedError()
