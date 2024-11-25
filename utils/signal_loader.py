from abc import ABC, abstractmethod
import wfdb
import numpy as np

class SignalReader(ABC):
    def __init__(self, ):
        self.signal = None
        self.window_size = None
        self.window_step = None
        self.current_position = 0

    def configure_reader(self, signal_path: str, window_size: int, window_step: int):
        self.signal = self.read_signal(signal_path)
        self.window_size = window_size
        self.window_step = window_step
        self.last_window_index = (len(self.signal) - self.window_size) // self.window_step

    def clear_reader(self):
        self.signal = None
        self.window_size = None
        self.window_step = None
        self.current_position = 0

    @abstractmethod
    def read_signal(self, signal_path: str) -> list[int]:
        pass

    def stream_normalized_signal(self):
        while self.current_position + self.window_size <= len(self.signal):
            window = self.signal[self.current_position:self.current_position + self.window_size]
            normalized_window = self._normalize_window(window)
            self.current_position += self.window_step
            yield normalized_window

    def reset_position(self):
        """Resets the current position to start streaming from the beginning."""
        self.current_position = 0

    def go_back(self):
        """Moves the current position back by one window step."""
        self.current_position = max(0, self.current_position - self.window_step*2)

    def position_to_index(self) -> int:
        return (self.current_position//self.window_step)-1

    def _normalize_window(self, window: list[int]) -> list[float]:
        min_val = min(window)
        max_val = max(window)
        if max_val == min_val:
            return [0.0] * len(window)
        return [(value - min_val) / (max_val - min_val) for value in window]

class AppleWatchSignalReader(SignalReader):
    def read_signal(self, signal_path: str) -> list[int]:
        with open(signal_path, 'r') as f:
            data = f.read().split('\n')

        ecg_signal = [data_point[0] for data_point in [data_point.split(',') for data_point in data[13:]]][:-1]
        ecg_signal = [int(data_point) for data_point in ecg_signal]

        return ecg_signal

class PhysionetSignalReader(SignalReader):
    FILE_EXTENSIONS = ["atr", "dat", "hea"]

    def read_signal(self, signal_path: str) -> list[int]:
        if signal_path[-3:] in self.FILE_EXTENSIONS:
            signal_path = signal_path[:-4]

        record = wfdb.rdrecord(signal_path)
        return record.p_signal[:,1].astype(np.float32)


def get_signal_reader(reader_type: str) -> SignalReader:
    if reader_type == "apple":
        return AppleWatchSignalReader()
    elif reader_type == "physionet":
        return PhysionetSignalReader()
