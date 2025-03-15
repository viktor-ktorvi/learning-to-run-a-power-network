from dataclasses import dataclass, field

from hydra.core.config_store import ConfigStore

from src.config.environment.environment import EnvironmentConfig
from src.config.plotting.plotting import PlottingConfig
from src.config.positional_encodings.positional_encodings import (
    PositionalEncodingsConfig,
)


@dataclass
class Config:
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    plotting: PlottingConfig = field(default_factory=PlottingConfig)
    positional_encodings: PositionalEncodingsConfig = field(default_factory=PositionalEncodingsConfig)

    random_seed: int = 42


config_store = ConfigStore.instance()
config_store.store(name="config", node=Config)
