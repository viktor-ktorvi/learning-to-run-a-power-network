from typing import Any

import grid2op
import hydra
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import torch
from torch_geometric import seed_everything
from torch_geometric.data import Data
from torch_geometric.transforms import (
    AddLaplacianEigenvectorPE,
    Compose,
    LineGraph,
    ToUndirected,
)
from torch_geometric.utils import to_networkx, to_undirected

from src import CONFIGS_PATH
from src.config.config import Config
from src.plotting.utils import set_rcParams


def normalize_positions(pos: dict[Any, tuple[float, float]]) -> dict[Any, tuple[float, float]]:
    """
    Normalize (x, y) positions of a point cloud.

    Parameters
    ----------
    pos: dict[Any, tuple[float, float]]
        Positions.
    Returns
    -------
    normalized_pos: dict[Any, tuple[float, float]]
        Normalized positions.
    """
    x_vals = [p[0] for p in pos.values()]
    y_vals = [p[1] for p in pos.values()]

    def get_mean_and_std(vals: list[float]) -> tuple[float, float]:
        return float(np.mean(vals)), float(np.std(vals))

    x_mean, x_std = get_mean_and_std(x_vals)
    y_mean, y_std = get_mean_and_std(y_vals)

    def normalize(val: float, mean: float, std: float) -> float:
        return (val - mean) / std if std != 0.0 else val - mean

    for key in pos:
        pos[key] = (normalize(pos[key][0], x_mean, x_std), normalize(pos[key][1], y_mean, y_std))

    return pos


@hydra.main(version_base=None, config_path=str(CONFIGS_PATH), config_name="default")
def main(cfg: Config):
    """
    Visualizing some graph positional encodings, e.g., Laplacian positional encodings.

    Parameters
    ----------
    cfg: Config
        Config.

    Returns
    -------
    """
    set_rcParams(cfg)
    seed_everything(cfg.random_seed)
    num_components = cfg.positional_encodings.num_components

    environment = grid2op.make(cfg.environment.name)

    edge_index = np.concatenate(
        (environment.line_or_to_subid.reshape(1, -1), environment.line_ex_to_subid.reshape(1, -1)), axis=0
    )
    edge_index = to_undirected(torch.LongTensor(edge_index))

    pyg_graph = Data(edge_index=edge_index, num_nodes=environment.n_sub)
    pyg_graph = AddLaplacianEigenvectorPE(k=num_components)(pyg_graph)
    nx_graph = to_networkx(pyg_graph)

    pyg_line_graph = Compose([LineGraph(force_directed=True), ToUndirected()])(pyg_graph)
    pyg_line_graph = AddLaplacianEigenvectorPE(k=num_components)(pyg_line_graph)

    pos = {
        substation_id: substation_pos for substation_id, substation_pos in enumerate(environment.grid_layout.values())
    }

    pos = normalize_positions(pos)

    fig, axs = plt.subplots(3, num_components)
    fig.suptitle("Laplacian eigenvector encodings")

    for i in range(num_components):
        eigenvector_label = rf"$\phi_{{{i + 1}}}$"

        # laplacian eigenvectors on a node level
        ax_graph = axs[0, i] if num_components > 1 else axs[0]
        laplacian_eigenvector = pyg_graph.laplacian_eigenvector_pe.numpy()[:, i]
        nx.draw_networkx(
            nx_graph,
            pos,
            ax=ax_graph,
            arrows=False,
            node_color=laplacian_eigenvector,
            vmin=laplacian_eigenvector.min(),
            vmax=laplacian_eigenvector.max(),
            cmap="coolwarm",
        )
        ax_graph.set_title(eigenvector_label)
        ax_graph.axis("off")  # remove border
        ax_graph.set_aspect("auto")

        # laplacian eigenvectors of the line graph
        ax_line_graph = axs[1, i] if num_components > 1 else axs[1]
        line_graph_laplacian_eigenvector = pyg_line_graph.laplacian_eigenvector_pe.numpy()[:, i]
        nx.draw_networkx(
            nx_graph,
            pos,
            ax=ax_line_graph,
            arrows=False,
            node_color="black",
            edge_color=line_graph_laplacian_eigenvector,
            edge_vmin=line_graph_laplacian_eigenvector.min(),
            edge_vmax=line_graph_laplacian_eigenvector.max(),
            edge_cmap=plt.cm.coolwarm,
            width=cfg.positional_encodings.line_graph.line_width,
            node_size=cfg.positional_encodings.line_graph.node_size,
            with_labels=False,
        )
        ax_line_graph.set_title(f"line graph {eigenvector_label}")
        ax_line_graph.axis("off")  # remove border
        ax_line_graph.set_aspect("auto")

        # average of adjacent node level laplacian eigenvectors
        ax_line_average = axs[2, i] if num_components > 1 else axs[2]

        line_average_eigenvector = []
        for edge_idx in range(pyg_graph.num_edges):
            source_node = pyg_graph.edge_index[0][edge_idx].item()
            target_node = pyg_graph.edge_index[1][edge_idx].item()
            line_average_eigenvector.append(
                (laplacian_eigenvector[source_node] + laplacian_eigenvector[target_node]) / 2
            )

        line_average_eigenvector = np.array(line_average_eigenvector)
        nx.draw_networkx(
            nx_graph,
            pos,
            ax=ax_line_average,
            arrows=False,
            node_color="black",
            edge_color=line_average_eigenvector,
            edge_vmin=line_average_eigenvector.min(),
            edge_vmax=line_average_eigenvector.max(),
            edge_cmap=plt.cm.coolwarm,
            width=cfg.positional_encodings.line_graph.line_width,
            node_size=cfg.positional_encodings.line_graph.node_size,
            with_labels=False,
        )
        ax_line_average.set_title(f"{eigenvector_label} averaged between edge pairs")
        ax_line_average.axis("off")  # remove border
        ax_line_average.set_aspect("auto")

    plt.show()


if __name__ == "__main__":
    main()
