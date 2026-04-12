import random
from .player import Player
from .board import default_board, apply_snake_ladder

class SnakeLaddersGame:
    def __init__(self, player_names):
        self.board = default_board()
        self.players = [Player(i, name) for i, name in enumerate(player_names)]
        self.turn_idx = 0
        self.winner_pid = None
        self.die_last = None

    def current_player(self):
        return self.players[self.turn_idx]

    def next_turn(self):
        n = len(self.players)
        for i in range(1, n + 1):
            next_index = (self.turn_idx + i) % n
            if self.players[next_index].active:
                self.turn_idx = next_index
                return
        # if no active players, game can end here
        self.turn_idx = 0

    def roll_and_move(self):
        player = self.current_player()
        if not player.active:
            self.next_turn()
            return None

        die = random.randint(1, 6)
        self.die_last = die
        next_pos = player.position + die

        # must land exactly on 100 to win
        if next_pos > self.board.size:
            next_pos = player.position

        next_pos = apply_snake_ladder(next_pos, self.board)
        player.position = next_pos

        if player.position == self.board.size:
            self.winner_pid = player.pid

        self.next_turn()
        return die
