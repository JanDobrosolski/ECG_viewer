import numpy as np

class CircularBuffer:
    def __init__(self, size: int):
        self.size = size
        self.buffer = np.full(size, np.nan)
        self.index = 0

    def update(self, value: float) -> float:
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size

        return self.mean()

    def mean(self) -> float:
        non_nan_values = self.buffer[~np.isnan(self.buffer)]
        return np.mean(non_nan_values) if non_nan_values.size > 0 else None
