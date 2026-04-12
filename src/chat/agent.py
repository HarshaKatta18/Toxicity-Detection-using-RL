import os
import joblib
import numpy as np
from .moderation_env import ModerationEnv, ACTIONS, BINS

# Save Q-table in the models folder
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "models"))
Q_PATH = os.path.join(MODELS_DIR, "moderation_q.pkl")

class EpsGreedyAgent:
    """
    ε-greedy reinforcement learning agent for chat moderation.
    Learns from toxicity probabilities and warning history.
    """

    def __init__(self, epsilon=0.1, lr=0.2):
        # Initialize Q-table: [toxicity_bin][warnings_0or1][action]
        self.Q = np.zeros((len(BINS) - 1, 2, len(ACTIONS)), dtype=np.float32)
        self.epsilon = epsilon
        self.lr = lr
        self.env = ModerationEnv()

        # Try loading an existing model (to persist learning)
        if os.path.exists(Q_PATH):
            try:
                self.Q = joblib.load(Q_PATH)
            except Exception:
                pass

    def act(self, proba_toxic: float, warnings: int):
        """
        Choose an action based on toxicity and warnings.
        Occasionally explore random actions (ε-greedy).
        """
        tox_bin = self.env.bin_prob(proba_toxic)
        warn_state = 1 if warnings > 0 else 0

        if np.random.rand() < self.epsilon:
            # Random action (exploration)
            return np.random.randint(len(ACTIONS))
        else:
            # Best action (exploitation)
            return int(np.argmax(self.Q[tox_bin, warn_state, :]))

    def update(self, proba_toxic: float, warnings: int, action: int, is_toxic_label: int):
        """
        Update Q-table after each moderation decision.
        """
        state, reward = self.env.step(proba_toxic, warnings, action, is_toxic_label)
        old_q = self.Q[state.tox_bin, state.warnings, action]
        td_target = reward  # no next state value (contextual bandit)
        self.Q[state.tox_bin, state.warnings, action] = old_q + self.lr * (td_target - old_q)

    def save(self):
        """Save Q-table for persistence."""
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(self.Q, Q_PATH)
