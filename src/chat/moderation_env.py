import numpy as np
from dataclasses import dataclass

# Define actions
ACTIONS = ["allow", "warn", "kick"]  # index: 0, 1, 2
BINS = np.linspace(0.0, 1.0, 11)  # 10 bins for toxicity score

@dataclass
class ModState:
    tox_bin: int
    warnings: int  # 0 or 1

class ModerationEnv:
    """
    Simple reinforcement learning environment:
    State = (toxicity_bin, warnings_count)
    Action = allow / warn / kick
    Reward = based on action correctness
    """

    def __init__(self):
        pass

    def bin_prob(self, p: float) -> int:
        """Convert toxicity probability to a discrete bin."""
        return int(np.digitize([p], BINS)[0] - 1)

    def step(self, proba_toxic: float, warnings: int, action: int, is_toxic_label: int):
        """
        Returns next state and reward for the action.
        """
        tb = self.bin_prob(proba_toxic)
        state = ModState(tb, 1 if warnings > 0 else 0)

        # Reward shaping
        if ACTIONS[action] == "allow":
            reward = 0 if is_toxic_label == 0 else -1.0
            if warnings > 0 and is_toxic_label == 1:
                reward -= 0.5
        elif ACTIONS[action] == "warn":
            reward = -0.2 if is_toxic_label == 0 else 0.3
        else:  # kick
            reward = -0.5 if is_toxic_label == 0 else 0.6

        return state, reward
