import matplotlib

from src.config.config import Config


def set_rcParams(cfg: Config):
    """
    Set matplotlib parameters.

    Parameters
    ----------
    cfg: Config
        Config.
    Returns
    -------
    """
    matplotlib.rcParams["figure.autolayout"] = True
    matplotlib.rcParams["figure.figsize"] = cfg.plotting.figure.figsize
    matplotlib.rcParams["figure.dpi"] = cfg.plotting.figure.dpi
    matplotlib.rcParams["font.size"] = cfg.plotting.font.size
