import pprint

import numpy as np
from grid2op import Observation
from grid2op.Agent import DoNothingAgent
from grid2op.Environment import Environment
from grid2op.PlotGrid import PlotMatplot
from tqdm import tqdm


class Game:
    """A class that keeps the state of the game, e.g., the state of the power grid simulation."""

    action_dict: dict
    rho_threshold: float = 0.99

    cumulative_reward: float = 0.0
    reward: float = 0.0
    info: dict = {}

    def __init__(self, environment: Environment):
        self.environment = environment
        self.clear_action_dict()

        self.plotter = PlotMatplot(environment.observation_space)

        self.observation = environment.reset()

    def clear_action_dict(self):
        """
        Clear the action dictionary.

        Returns
        -------
        """
        self.action_dict = {"set_bus": {"lines_or_id": [], "lines_ex_id": [], "generators_id": [], "loads_id": []}}

    def print_action_dict(self):
        """
        Print the action dictionary.

        Returns
        -------
        """
        # TODO could also print the status of the elements

        line_indices_str = ""
        line_or_to_subid_str = ""
        line_ex_to_subid_str = ""

        idx_formatting = "4d"

        for i in np.arange(self.environment.n_line):
            line_indices_str += f"{i:{idx_formatting}}"
            line_or_to_subid_str += f"{self.environment.line_or_to_subid[i]:{idx_formatting}}"
            line_ex_to_subid_str += f"{self.environment.line_ex_to_subid[i]:{idx_formatting}}"

        gen_indices_str = ""
        gen_to_subid_str = ""
        for i in np.arange(self.environment.n_gen):
            gen_indices_str += f"{i:{idx_formatting}}"
            gen_to_subid_str += f"{self.environment.gen_to_subid[i]:{idx_formatting}}"

        load_indices_str = ""
        load_to_subid_str = ""
        for i in np.arange(self.environment.n_load):
            load_indices_str += f"{i:{idx_formatting}}"
            load_to_subid_str += f"{self.environment.load_to_subid[i]:{idx_formatting}}"

        name_formatting = "20"

        dashes = "".join(["-"] * 100)
        print(
            f"{'Line ID:':{name_formatting}}{line_indices_str}\n\n"
            f"{'line_or_to_subid:':{name_formatting}}{line_or_to_subid_str}\n"
            f"{'line_ex_to_subid:':{name_formatting}}{line_ex_to_subid_str}\n\n"
            f"{dashes}\n"
            f"{'Generator ID:':{name_formatting}}{gen_indices_str}\n\n"
            f"{'gen_to_subid:':{name_formatting}}{gen_to_subid_str}\n\n"
            f"{dashes}\n"
            f"{'Load ID:':{name_formatting}}{load_indices_str}\n\n"
            f"{'load_to_subid:':{name_formatting}}{load_to_subid_str}\n\n"
            f"{dashes}\n"
        )

        print("\nSelected actions: ", end="")
        pp = pprint.PrettyPrinter(depth=10)
        pp.pprint(self.action_dict)
        print()

    def get_substation_ids(self) -> list[int]:
        """
        Get a list of all substation IDs.

        Returns
        -------
        substation_ids: list[int]
            List of substation IDs.
        """
        return list(range(self.environment.n_sub))

    def get_busbar_options(self) -> list[int]:
        """
        Get a list of possible busbar states.

        Returns
        -------
        busbar_options: list[int]
            List of possible busbar states.
        """
        return list(range(1, self.environment.n_busbar_per_sub + 1))

    def print_info(self):
        """
        Print the information and reward received after stepping through the environment.

        Returns
        -------
        """
        print(f"Action reward: {self.reward}")
        print("\nInfo: ", end="")
        pp = pprint.PrettyPrinter(depth=10)
        pp.pprint(self.info)

    def continue_simulation(self, initial_action_dict: dict) -> tuple[Observation, float, bool, dict]:
        """
        Continue the simulation. Apply an initial action, then keep doing nothing until any of the lines become
        overloaded. At that point stop and return some information.

        Parameters
        ----------
        initial_action_dict: dict
            Initial action dictionary.

        Returns
        -------
        observation: Observation
            Observation.
        reward: float
            Reward.
        done: bool
            Done signal.
        info: dict
            Information dictionary.
        """
        do_nothing_agent = DoNothingAgent(self.environment.action_space)

        def while_loop():
            while True:
                yield

        # TODO is it possible to start from random points in time?

        initial_action_flag = True
        progress_bar = tqdm(while_loop())
        for _ in progress_bar:
            if initial_action_flag:
                action = self.environment.action_space(initial_action_dict)
                initial_action_flag = False
            else:
                action = do_nothing_agent.act(None, 0, False)

            observation, reward, done, info = self.environment.step(action)

            self.observation = observation
            self.info = info
            self.reward = reward

            self.cumulative_reward += reward

            progress_bar.set_description(
                f"Running simulation "
                f"{str(observation.day).zfill(2)}/{str(observation.month).zfill(2)}/{str(observation.year)} "
                f"{str(observation.hour_of_day).zfill(2)}:{str(observation.minute_of_hour).zfill(2)} "
                f"Cumulative reward = {self.cumulative_reward} "
                f"Reward = {reward}"
            )

            if done:
                # TODO got this even though the threshold didn't trigger
                #  what triggers the done signal exactly?

                self.print_info()

                raise RuntimeError(f"Done signal was True. Cumulative reward = {self.cumulative_reward}")

            if (observation.rho >= self.rho_threshold).any():
                return observation, reward, done, info
