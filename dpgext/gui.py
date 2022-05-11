import dearpygui.dearpygui as dpg
from dpgext.elements import UpdatableElement

from dpgext.window import Window
from utils.logger import LOGGER

class Gui:
    _instance = None # Singleton instance    

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Gui, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._running = False
        self.windows: dict[str, Window] = {}
        pass

    def _tick(self):
        for window in self.windows.values():
            window.update()
            
        UpdatableElement.update_all()
        pass

    def _setup(self):
        DECORATED = True
        viewport_title = 'Config GUI'
        # Initialize the gui
        LOGGER.log_info("Starting GUI...", 'GUI')
        LOGGER.log_trace("Initializing DPG stuff...", 'GUI')
        dpg.create_context()
        dpg.configure_app(docking=True, docking_space=True, auto_save_init_file=True, init_file='config_gui.ini')
        dpg.create_viewport(title=viewport_title, decorated=DECORATED)
        dpg.setup_dearpygui()
        # wmargin = BORDER_PIXELS if DECORATED else 2 * BORDER_PIXELS
        # vpad = TITLEBAR_PIXELS + BORDER_PIXELS if DECORATED else 2*BORDER_PIXELS
        # dpg.set_viewport_pos([1600 + wmargin, 0])
        # dpg.set_viewport_width(1920-1600)
        # dpg.set_viewport_height(900 + vpad)
        dpg.show_viewport()

        self._setup_theme()
        self._setup_fonts()
        
        self._init_windows()

    def _setup_theme(self):
        pass

    def _setup_fonts(self):
        # with dpg.font_registry(show=False):
        #     fid = dpg.add_font('fonts/OpenSans-VariableFont_wdth,wght.ttf', size=16)
        # dpg.bind_font(fid)
        pass

    def _init_windows(self):
        pass

    def _describe_windows(self):
        for name, window in self.windows.items():
            window.describe()
            pass

    def _describe_menu(self):
        with dpg.viewport_menu_bar(show=True, tag='menu_bar'):
            with dpg.menu(label='Windows', parent='menu_bar', tag='windows_menu'):
                for name, window in self.windows.items():
                    label = window.kwargs.get('label', name)
                    dpg.add_menu_item(label=label, parent='windows_menu', callback=window.show, tag=f'{name}_menu_item')
                    pass
                pass


            with dpg.menu(label="Debug Windows"):
                dpg.add_menu_item(label="About", callback=dpg.show_about)
                dpg.add_menu_item(label="Metrics", callback=dpg.show_metrics)
                dpg.add_menu_item(label="Style Editor", callback=dpg.show_style_editor)
                dpg.add_menu_item(label="Font Manager", callback=dpg.show_font_manager)
                dpg.add_menu_item(label="Debug", callback=dpg.show_debug)
                dpg.add_menu_item(label="Documentation", callback=dpg.show_documentation)
                dpg.add_menu_item(label="Item Registry", callback=dpg.show_item_registry)
                dpg.add_menu_item(label="Imgui Demo", callback=dpg.show_imgui_demo)
                dpg.add_menu_item(label="Implot Demo", callback=dpg.show_implot_demo)
                dpg.add_menu_item(label="Item Debug", callback=dpg.show_item_debug)
            pass

    def _on_started(self):
        pass

    def _on_exiting(self):
        pass

    def run(self):
        self._setup()

        self._running = True
        self._describe_windows()
        self._describe_menu()

        self._on_started()

        while dpg.is_dearpygui_running() and self._running:
            self._tick()
            dpg.render_dearpygui_frame()

        self._running = False
        self._on_exiting()
        dpg.destroy_context()