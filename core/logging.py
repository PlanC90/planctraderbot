from typing import List


class UILogBuffer:
    def __init__(self, max_lines: int = 500):
        self.max_lines = max_lines
        self.buffer: List[str] = []

    def append(self, entry: str) -> None:
        self.buffer.append(entry)
        if len(self.buffer) > self.max_lines:
            self.buffer = self.buffer[-self.max_lines:]

    def get_all(self) -> List[str]:
        return list(self.buffer)



