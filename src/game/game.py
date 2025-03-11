import pprint

import numpy as np
from grid2op import Observation
from grid2op.Agent import DoNothingAgent
from grid2op.Environment import Environment
from grid2op.PlotGrid import PlotMatplot
from tqdm import tqdm


# TODO docs
class Game:
    action_dict: dict
    rho_threshold: float = 0.99

    cumulative_reward: float = 0.0

    def __init__(self, environment: Environment):
        self.environment = environment
        self.clear_action_dict()

        self.plotter = PlotMatplot(environment.observation_space)

        self.observation = environment.reset()

    def clear_action_dict(self):
        self.action_dict = {"set_bus": {"lines_or_id": [], "lines_ex_id": [], "generators_id": [], "loads_id": []}}

    def print_action_dict(self):
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
        return list(range(self.environment.n_sub))

    def get_busbar_options(self) -> list[int]:
        return list(range(1, self.environment.n_busbar_per_sub + 1))

    def continue_simulation(self, initial_action_dict: dict) -> Observation:
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
                raise RuntimeError(f"Failed to run a power network. Cumulative reward = {self.cumulative_reward}")

            if (observation.rho >= self.rho_threshold).any():
                return observation
