from dataclasses import dataclass

@dataclass(frozen=True)
class BoardConfig:
    size: int = 100
    snakes: dict = None
    ladders: dict = None

def default_board():
    snakes = {
        16: 6,
        47: 26,
        49: 11,
        56: 53,
        62: 19,
        64: 60,
        87: 24,
        93: 73,
        95: 75,
        98: 78,
        99: 40,
    }
    ladders = {
        2: 38,
        4: 25,
        9: 31,
        21: 42,
        28: 84,
        36: 44,
        51: 72,
        71: 91,
        79: 97,
    }
    return BoardConfig(size=100, snakes=snakes, ladders=ladders)

def apply_snake_ladder(position: int, cfg: BoardConfig) -> int:
    """Check if the current position has a snake or ladder."""
    if position in cfg.snakes:
        return cfg.snakes[position]
    if position in cfg.ladders:
        return cfg.ladders[position]
    return position
