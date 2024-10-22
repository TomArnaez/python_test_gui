from typing import List
from numpy.typing import NDArray

import numpy as np

def sl_error_to_exception(error: SLError):
    if error != 0:
        raise RuntimeError("Got SLError")

def run_sequence_capture(device: SLDevice, num_frames: int, exp_time: int) -> List[NDArray[np.uint16]]:
    error: SLError = 0

    sl_error_to_exception(device.SetNumberOfFrames(num_frames))
    sl_error_to_exception(device.SetExposureTime(exp_time))
    sl_error_to_exception(device.StartStream())

    sl_error_to_exception(device.StopStream())