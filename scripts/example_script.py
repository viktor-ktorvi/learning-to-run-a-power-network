import pprint

import hydra
from omegaconf import OmegaConf

from src import CONFIGS_PATH
from src.config.config import Config


@hydra.main(version_base=None, config_path=str(CONFIGS_PATH), config_name="default")
def main(cfg: Config):
    """
    An example script.

    Parameters
    ----------
    cfg: Config
        Config.

    Returns
    -------
    """
    print("Hello world\n")
    print("Config:")
    pp = pprint.PrettyPrinter(depth=10)
    pp.pprint(OmegaConf.to_container(cfg))


if __name__ == "__main__":
    main()
