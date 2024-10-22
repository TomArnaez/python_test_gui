from typing import Union
from tests.tests import Test, TestType
import dearpygui.dearpygui as dpg

def create_test_element(test: Test, parent: Union[int, str]):
    match test.test_type:
        case TestType.DARK_CURRENT:
            dpg.add_input_int(
                label="Lower exposure time",
                default_value=test.params.lower_exp_time,
                callback=lambda sender, app_data, user_data: setattr(test, "lower_exp_time", app_data),
            )
            dpg.add_input_int(
                label="Upper exposure time",
                default_value=test.params.upper_exp_time,
                callback=lambda sender, app_data, user_data: setattr(test, "upper_exp_time", app_data),
            )
            dpg.add_input_int(
                label="Number of iterations",
                default_value=test.params.iteration_settings.num_iterations,
                callback=lambda sender, app_data, user_data: setattr(test.iteration_settings, "num_iterations", app_data),
            )
            dpg.add_input_int(
                label="Minutes between iterations",
                default_value=test.params.iteration_settings.iteration_time_mins,
                callback=lambda sender, app_data, user_data: setattr(test.iteration_settings, "iteration_time_mins", app_data),
            )
        case TestType.OFFSET_DRIFT:
            pass
        case TestType.BLINKING_PIXEL:
            # Implement logic for BLINKING_PIXEL
            pass