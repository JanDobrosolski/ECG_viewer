import heartpy as hp
import numpy as np

from abc import ABC, abstractmethod

from utils.model_loader import load_E2E_Model
from utils.circular_buffer import CircularBuffer

class SignalAnalyser(ABC):
   def __init__(self, sampling_frequency, monitoring_buffer_size):
       self.sampling_frequency = sampling_frequency
       self.buffer = CircularBuffer(monitoring_buffer_size)
       
   @abstractmethod
   def calculate_RMSSD(self, signal: list[float]) -> float:
       pass


class HPSignalAnalyser(SignalAnalyser):
    def calculate_RMSSD(self, signal: list[float]) -> float:
        _, m = hp.process(hp.scale_data(signal), self.sampling_frequency)
        rmssd = m['rmssd']

        return round(rmssd, 2)


class DLSignalAnalyser(SignalAnalyser):
    def __init__(self, sampling_frequency, monitoring_buffer_size, model_path):
        super().__init__(sampling_frequency, monitoring_buffer_size)
        self.model = load_E2E_Model(model_path)

    def calculate_RMSSD(self, signal: list[float]) -> float:
        signal = np.array(signal)
        signal = signal.reshape((1, signal.shape[0], 1))

        rmssd = self.model(signal).numpy()[0][0]

        return round(rmssd, 2)
