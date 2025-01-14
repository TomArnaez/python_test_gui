from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
import logging
from pathlib import Path
import time
from typing import Dict, Generic, List, Optional, Type, TypeVar
from enum import Enum
from numpy.typing import NDArray
import numpy as np

from detector import sequence_capture
from tests.io import save_tiff_stack

class TestType(Enum):
    DARK_CURRENT = "dark_current"
    OFFSET_DRIFT = "offset_drift"
    BLINKING_PIXEL = "blinking_pixel"

class TestResult(ABC):
    """Abstract base class for all test results."""

    @property
    @abstractmethod
    def test_type(self) -> TestType:
        """Return the unique identifier for the test."""
        pass

    @abstractmethod
    def save_frame_data(self, base_path: Path):
        """Optionally save frame data if available."""
        pass

R = TypeVar('R', bound=TestResult)

class Test(ABC, Generic[R]):
    @property
    @abstractmethod
    def test_type(self) -> TestType:
        """Return the unique identifier for the test."""
        pass

    @abstractmethod
    def run(self, device: SLDevice, keep_frame_data: bool = True) -> R:
        """Execute the test and return the result."""
        pass

test_registry: Dict[str, Type[Test]] = {}

def register_test(test_name: str):
    def decorator(test_class: Type[Test]):
        test_registry[test_name] = test_class
        return test_class
    return decorator

@dataclass
class IterationSettings:
    num_iterations: int
    iteration_wait_time_mins: int 

@dataclass
class DarkCurrentDataPoint:
    temperature: float
    dark_current_adu_per_ms: float

@dataclass
class DarkCurrentFrameData:
    upper_exp_time_frames: List[NDArray[np.uint16]]
    lower_exp_time_frames: List[NDArray[np.uint16]]

@dataclass
class DarkCurrentTestParams:
    lower_exp_time: int
    upper_exp_time: int
    frames_per_sequence: int
    iteration_settings: IterationSettings

@dataclass
class DarkCurrentTestResult(TestResult):
    params: DarkCurrentTestParams
    dark_current_data: List[DarkCurrentDataPoint]
    dark_current_frame_data: Optional[DarkCurrentFrameData]

    @property
    def test_type(self) -> TestType:
        return TestType.DARK_CURRENT
    
    def to_dict(self):
        return {
            'params': asdict(self.params),
            'dark_current_data': [asdict(data_point) for data_point in self.dark_current_data],
        }

    def save_frame_data(self, base_path: Path):
        if self.dark_current_frame_data is None:
            raise ValueError("Frame data not available")

        base_path.mkdir(parents=True, exist_ok=True)

        lower_exp_tiff_path = base_path / f"lower_exp_time_{self.params.lower_exp_time}_ms.stack.tiff"
        save_tiff_stack(self.dark_current_frame_data.lower_exp_time_frames, lower_exp_tiff_path)

        upper_exp_tiff_path = base_path / f"upper_exp_time_{self.params.upper_exp_time}_ms_stack.tiff"
        save_tiff_stack(self.dark_current_frame_data.upper_exp_time_frames, upper_exp_tiff_path)

@dataclass
@register_test("Dark Current")
class DarkCurrentTest(Test[DarkCurrentTestResult]):
    params: DarkCurrentTestParams = field(default_factory=lambda: DarkCurrentTestParams(1000, 10000, IterationSettings(1, 0)))

    @property
    def test_type(self) -> TestType:
        return TestType.DARK_CURRENT

    def run(self, device: SLDevice, keep_frame_data: bool = True) -> DarkCurrentTestResult:
        dark_currents: List[DarkCurrentDataPoint] = []
        dark_current_frame_data: Optional[DarkCurrentFrameData] = None

        if (keep_frame_data):
            dark_current_frame_data = DarkCurrentFrameData([], [])

        for i in range(self.params.iteration_settings.num_iterations):
            lower_exp_frame = sequence_capture(device, self.params.frames_per_sequence, self.params.lower_exp_time)
            upper_exp_frame = sequence_capture(device, self.params.frames_per_sequence, self.params.upper_exp_time)

            if (keep_frame_data):
                dark_current_frame_data.lower_exp_time_frames.append(lower_exp_frame)
                dark_current_frame_data.upper_exp_time_frames.append(upper_exp_frame)

            result = lower_exp_frame.astype(np.int32) - upper_exp_frame.astype(np.int32)
            mean = result.mean()
            dark_current = mean / float(self.params.upper_exp_time - self.params.lower_exp_time)
            temperature = 0.0

            dark_currents.append(DarkCurrentDataPoint(temperature, dark_current))
            
            logging.debug(f"Waiting for {self.params.iteration_settings.iteration_wait_time_mins} minutes")
            time.sleep(float(self.params.iteration_settings.iteration_wait_time_mins) / 60.0)

        return DarkCurrentTestResult(self.params, dark_currents, dark_current_frame_data)
    
@dataclass
class OffsetDriftTestResult:
    adus: List[int]

@dataclass
@register_test("Offset Drift")
class OffsetDriftTest(Test[OffsetDriftTestResult]):
    exp_times: List[int] =  field(default_factory=lambda: [])
    iteration_settings: IterationSettings = field(default_factory=lambda: IterationSettings(num_iterations=1, iteration_time_mins=0))

    @property
    def test_type(self) -> TestType:
        return TestType.OFFSET_DRIFT

@dataclass
class BlinkingPixelTestResult:
    exp_time: int

@dataclass
@register_test("Blinking Pixel")
class BlinkingPixelTest(Test[BlinkingPixelTestResult]):
    type = TestType.BLINKING_PIXEL
    exp_time: List[int]

    @property
    def test_type(self) -> TestType:
        return TestType.BLINKING_PIXEL