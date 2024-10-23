from dataclasses import dataclass
from enum import Enum
import time
from typing import Generator, List

from detector.helper import sl_error_to_exception
from tests.test_result_manager import TestResultManager
from tests.tests import Test

class Core:
    def __init__(self):
        self.device: SLDevice
        self.test_manager: TestManager = TestManager()
        self.test_result_manager: TestResultManager = TestResultManager()

        sl_error_to_exception(device.OpenCamera())

    def __del__(self):
        sl_error_to_exception(device.CloseCamera())

class TestEventType(Enum):
    RUNNING = "running"
    FINISHED = "finished"

@dataclass
class TestEvent:
    type: TestEventType
    subtask_name: str = ""
    progress: int = 1

class TestManager:
    def __init__(self):
        self.selected_tests: List[Test] = []

    def add_test(self, test: Test):
        self.selected_tests.append([test])

    def remove_test(self, test: Test):
        self.selected_tests.remove(test)

    def run_tests(self, device: SLDevice) -> Generator[TestEvent, None, None]:
        total_tests = len(self.selected_tests)
        for index, test in enumerate(self.selected_tests):
            progress = (index) / total_tests
            yield TestEvent(TestEventType.RUNNING, "placeholder", progress)
            time.sleep(5)

        yield TestEvent(TestEventType.FINISHED)