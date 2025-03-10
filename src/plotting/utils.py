import matplotlib
from omegaconf import DictConfig


def set_rcParams(cfg: DictConfig):
    """
    Set matplotlib parameters.

    Parameters
    ----------
    cfg
        Config.
    Returns
    -------
    """
    matplotlib.rcParams["figure.autolayout"] = True
    matplotlib.rcParams["figure.figsize"] = cfg.plotting.figure.figsize
    matplotlib.rcParams["figure.dpi"] = cfg.plotting.figure.dpi
    matplotlib.rcParams["font.size"] = cfg.plotting.font.size
