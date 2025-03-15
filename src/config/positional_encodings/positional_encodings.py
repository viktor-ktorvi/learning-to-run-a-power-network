from dataclasses import dataclass, field


@dataclass
class LineGraphConfig:
    line_width: int = 5
    node_size: int = 50


@dataclass
class PositionalEncodingsConfig:
    line_graph: LineGraphConfig = field(default_factory=LineGraphConfig)
    num_components: int = 3
