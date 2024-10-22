import threading
from gui.test_elements import create_test_element
from tests.test_manager import TestManager
import dearpygui.dearpygui as dpg
from tests.tests import test_registry

class GUIApp:
    def __init__(self):
        self.rows = []
        self.test_manager = TestManager()

    def run_gui(self):
        dpg.create_context()
        with dpg.window(label="Test Selection", width = 800, height = 600):
            test_names = list(test_registry.keys())

            with dpg.group() as self.main_group:
                dpg.add_combo(label="Add Test", items=test_names, callback=self.add_test)

                with dpg.table(header_row=True, reorderable=True) as self.table_id:
                    dpg.add_table_column(label="Test Name")
                    dpg.add_table_column(label="Action")

                dpg.add_button(label="Run Tests", callback=self.run_tests)

            self.progress_bar = dpg.add_progress_bar(label="Progress", default_value=0.0, show=False)

        dpg.create_viewport(title="Test Selection", width=1024, height=800)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def add_test(self, _, app_data):
        selected_test_name = app_data
        test_class = test_registry[selected_test_name]
        test_instance = test_class()

        with dpg.table_row(parent=self.table_id) as row_id:
            with dpg.table_cell():
                with dpg.collapsing_header(label=selected_test_name):
                    create_test_element(test_instance, parent=dpg.last_item())
            with dpg.table_cell():
                dpg.add_button(label="Remove", callback=self.remove_row, user_data=(row_id, selected_test_name))

        self.test_manager.add_test(test_instance)

    def remove_row(self, sender, app_data, user_data):
        row, test_name = user_data
        dpg.delete_item(row)
        self.rows.remove(row)

        self.test_manager.remove_test(test_name)

    def run_tests(self):
        self.disable_gui()
        threading.Thread(target=self.run_tests_thread).start()

    def run_tests_thread(self):
        for event in self.test_manager.run_tests():
            dpg.set_value(self.progress_bar, event.progress)
        self.enable_gui()

    def disable_gui(self):
        dpg.configure_item(self.main_group, enabled=False)
        dpg.configure_item(self.progress_bar, show=True)
        
    def enable_gui(self):
        dpg.configure_item(self.main_group, enabled=True)
        dpg.configure_item(self.progress_bar, show=False)