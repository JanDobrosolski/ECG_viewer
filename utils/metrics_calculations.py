import numpy as np

def calculate_rmssd(peak_indices: list[int], sampling_rate: int) -> float:
    
    ibi = np.diff(peak_indices)  # time difference between peaks in samples
    ibi_ms = (ibi / sampling_rate) * 1000  # convert to milliseconds

    diff_ibi = np.diff(ibi_ms)
    squared_diffs = np.square(diff_ibi)

    mean_squared_diff = np.mean(squared_diffs)

    return np.sqrt(mean_squared_diff).astype(float)
