class Player:
    def __init__(self, pid: int, name: str):
        self.pid = pid
        self.name = name
        self.position = 1
        self.active = True   # becomes False if kicked
        self.warnings = 0

    def reset(self):
        self.position = 1
        self.active = True
        self.warnings = 0
