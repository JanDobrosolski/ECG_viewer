import os
import json
import matplotlib.pyplot as plt

from typing import Callable

from utils.metrics_calculations import calculate_rmssd


def onclick_tagging(peaks: list[tuple[int, float]], ax: plt.Axes) -> Callable:
    original_xlim = ax.get_xlim()
    original_ylim = ax.get_ylim()
    # The actual event handler function
    def handle_click(event):
        if event.key == 'shift' and event.xdata and event.ydata:
            peaks.append(round(event.xdata))
            print(f"Peak tagged at: x = {event.xdata}")

            # Plot the clicked point on the graph
            plt.plot(event.xdata, event.ydata, 'ro')
            plt.draw()

            ax.set_xlim(original_xlim)
            ax.set_ylim(original_ylim)
            plt.draw()

    return handle_click

class TaggedSignal:
    def __init__(self, signal: list[float], peaks: list[tuple[int, float]] = [], rmssd: float = None):
        self.signal = signal
        self.peaks = peaks
        self.rmssd = None
    
    def to_dict(self) -> dict:
        return {
            "signal": self.signal,
            "peaks": self.peaks,
            "rmssd": self.rmssd
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaggedSignal':
        signal = data['signal']
        peaks = data['peaks']
        rmssd = data.get('rmssd', None)

        return cls(signal, peaks, rmssd)

    def save_to_json(self, dir_path: str, filename: str) -> None:
        os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, filename)
        
        with open(filepath, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

    @classmethod
    def load_from_json(cls, filepath: str) -> 'TaggedSignal':
        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
        return cls.from_dict(data)
    
    def tag_window(self, sampling_rate):
        fig, ax = plt.subplots()
        plt.plot(self.signal)
        _ = fig.canvas.mpl_connect('button_press_event', onclick_tagging(self.peaks, ax))

        plt.show()

        self.rmssd = calculate_rmssd(self.peaks, int(sampling_rate))
