from importlib import resources
import io
import dearpygui.dearpygui as dpg

def hello():
    print("Hello, world!")


def window():
    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    dpg.show_viewport()

    dpg.show_imgui_demo()

    dpg.start_dearpygui()

    dpg.destroy_context()
