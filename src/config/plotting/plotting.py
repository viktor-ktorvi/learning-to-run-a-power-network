from dataclasses import dataclass, field


@dataclass
class FigureConfig:
    figsize: tuple[float, float] = (16, 9)
    dpi: float = 130.0


@dataclass
class FontConfig:
    size: int = 14


@dataclass
class PlottingConfig:
    figure: FigureConfig = field(default_factory=FigureConfig)
    font: FontConfig = field(default_factory=FontConfig)
    subplot_title_fontsize: int = 13
