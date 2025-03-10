import grid2op
import hydra
from grid2op.PlotGrid import PlotMatplot
from matplotlib import pyplot as plt
from omegaconf import DictConfig

from src import CONFIGS_PATH
from src.game.game import Game
from src.plotting.utils import set_rcParams


@hydra.main(version_base=None, config_path=str(CONFIGS_PATH), config_name="default")
def main(cfg: DictConfig):
    """
    An example of running grid2op.

    Parameters
    ----------
    cfg: DictConfig
        Config.

    Returns
    -------
    """
    set_rcParams(cfg)

    environment = grid2op.make("l2rpn_case14_sandbox")
    plot_helper = PlotMatplot(environment.observation_space)

    game = Game(environment)

    observation = game.continue_simulation({})
    fig = plt.figure()
    plot_helper.plot_obs(observation, figure=fig)
    plt.gcf().suptitle("Grid")
    plt.show()


if __name__ == "__main__":
    main()
