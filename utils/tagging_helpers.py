import os
import json
import matplotlib.pyplot as plt

from typing import Callable


def onclick_tagging(peaks: list[tuple[int, float]]) -> Callable:
    # The actual event handler function
    def handle_click(event):
        if event.key == 'shift' and event.xdata and event.ydata:
            peaks.append((round(event.xdata), event.ydata))
            print(f"Peak tagged at: x = {event.xdata}, y = {event.ydata}")

            # Plot the clicked point on the graph
            plt.plot(event.xdata, event.ydata, 'ro')
            plt.draw()
    return handle_click

class TaggedSignal:
    def __init__(self, signal: list[float], peaks: list[tuple[int, float]] = []):
        self.signal = signal
        self.peaks = peaks
    
    def to_dict(self) -> dict:
        return {
            "signal": self.signal,
            "peaks": [{"x": x, "y": y} for x, y in self.peaks]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaggedSignal':
        signal = data['signal']
        peaks = [(peak['x'], peak['y']) for peak in data['peaks']]
        return cls(signal, peaks)

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
    
    def tag_window(self):
        fig, ax = plt.subplots()
        plt.plot(self.signal)
        _ = fig.canvas.mpl_connect('button_press_event', onclick_tagging(self.peaks))

        plt.show()
