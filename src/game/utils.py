import ipywidgets
import numpy as np
from grid2op.Environment import Environment

# TODO docs


class Outputs:
    action: ipywidgets.Output = ipywidgets.Output()
    plot: ipywidgets.Output = ipywidgets.Output()


def get_line_id(environment: Environment, substation_id: int, line_destination: int) -> tuple[np.array, np.array]:
    line_or_mask = (environment.line_or_to_subid == substation_id) & (environment.line_ex_to_subid == line_destination)
    line_ex_mask = (environment.line_ex_to_subid == substation_id) & (environment.line_or_to_subid == line_destination)

    line_or_idx = np.argwhere(line_or_mask)
    line_ex_idx = np.argwhere(line_ex_mask)

    return line_or_idx, line_ex_idx


def get_busbar_status(element_idx: int, action_list: list[tuple[int, int]], element_busbar_statuses: np.array):
    """
    Get the status of a given busbar. If an action has been performed return the status after the action, otherwise read
    the status from the environment observation.

    Parameters
    ----------
    element_idx: int
        Line index.
    action_list: list[tuple[int, int]]
        List of actions performed.
    element_busbar_statuses: np.array
        Numpy array containing the status of busbars of the elements.

    Returns
    -------
    busbar_status: int
        Busbar status.
    """
    for action_tuple in action_list:
        if action_tuple[0] == element_idx:
            return action_tuple[1]

    return element_busbar_statuses[element_idx]


def add_or_overwrite_action(
    new_action_tuple: tuple[int, int], action_list: list[tuple[int, int]], element_busbar_statuses: np.array
) -> list[tuple[int, int]]:
    """
    Add the new action tuple if the element being acted upon is not already there. Otherwise, overwrite the action for
    that element.

    Parameters
    ----------
    new_action_tuple: tuple[int, int]
        New action tuple (line_idx, busbar).
    action_list: list[tuple[int, int]]
        Action list.
    element_busbar_statuses: np.array
        Numpy array containing the status of the lines and their busbars.

    Returns
    -------
    updated_action_list: list[tuple[int, int]]
        Updated action list.
    """
    exists_flag = False
    for i in range(len(action_list)):
        if action_list[i][0] == new_action_tuple[0]:
            action_list[i] = new_action_tuple

            # if the action just reverts everything to the original state
            if element_busbar_statuses[new_action_tuple[0]] == new_action_tuple[1]:
                del action_list[i]

            exists_flag = True
            break

    # add action if it doesn't already exist and if it actually changes the current state
    if not exists_flag and element_busbar_statuses[new_action_tuple[0]] != new_action_tuple[1]:
        action_list.append(new_action_tuple)

    return action_list


DONT_CLICK_THIS = "Don't click this."
