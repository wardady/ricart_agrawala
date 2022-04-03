from enum import Enum


class ProcessState(Enum):
    DO_NOT_WANT = 1
    WANTED = 2
    HELD = 3

    def __str__(self):
        return self.name
