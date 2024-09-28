from abc import ABC, abstractmethod
import wfdb
import numpy as np

class SignalReader(ABC):
    @abstractmethod
    def read_signal(self, signal_path: str) -> list[int]:
        pass

    def stream_normalized_signal(self, signal_path: str, window_size: int, window_step: int):
        signal = self.read_signal(signal_path)

        for i in range(0, len(signal) - window_size + 1, window_step):
            window = signal[i:i + window_size]
            yield self._normalize_window(window)

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
    def read_signal(self, signal_path: str) -> list[int]:
        record = wfdb.rdrecord(signal_path)
        return record.p_signal[:,0].astype(np.float32)
