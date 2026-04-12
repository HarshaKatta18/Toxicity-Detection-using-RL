from game.game import SnakeLaddersGame

class ServerState:
    def __init__(self):
        # Create a new Snake & Ladders game with 4 players
        self.game = SnakeLaddersGame(["P1", "P2", "P3", "P4"])
        # Moderation data for each player: warnings and active status
        self.mod = {i: {"warnings": 0, "active": True} for i in range(4)}

    def reset(self, names):
        # Restart the game with new player names
        self.game = SnakeLaddersGame(names)
        self.mod = {i: {"warnings": 0, "active": True} for i in range(len(names))}
