from collections import namedtuple
from typing import Union

from utils.sig import metsig
from utils.logger import LOGGER
import dearpygui.dearpygui as dpg

class Container:
    def __init__(self, *args, id: Union[str,int] = 0, **kwargs):
        self.id = id
        self.added = False
        self.args = args
        self.kwargs = kwargs

    def _add(self) -> Union[str,int]:
        if type(self) is Container:
            raise NotImplementedError("Container is an abstract class")
        return ''
        
    def _add_if_needed(self):
        if not self.added:
            self.added = True
            self.id = self._add()

    def show(self):
        if not self.added:
            LOGGER.log_error("Container not added, cannot show", 'GUI.WINDOW')
            return
        dpg.show_item(self.id)

    def hide(self):
        if not self.added:
            LOGGER.log_error("Container not added, cannot hide", 'GUI.WINDOW')
            return
        dpg.hide_item(self.id)

    def toggle_visibility(self):
        if not self.added:
            LOGGER.log_error("Container not added, cannot toggle visibility", 'GUI.WINDOW')
            return
        if dpg.is_item_visible(self.id):
            self.hide()
        else:
            self.show()

    def clear(self):
        if self.added:
            dpg.delete_item(self.id, children_only=True)
        else:
            print("Container not added, cannot clear")

    def update(self):
        pass

    def __enter__(self):
        self._add_if_needed()
        dpg.push_container_stack(self.id)
        return self

    def __exit__(self, *args):
        dpg.pop_container_stack()
        pass    

class Group(Container):
    @metsig(dpg.group)
    def __init__(self, id: Union[str,int] = 0, *args, **kwargs):
        super().__init__(id=id, *args, **kwargs)

    def _add(self) -> Union[str,int]:
        super()._add()
        return dpg.add_group(id=self.id, *self.args, **self.kwargs)

    def describe(self):
        self.__enter__()
        dpg.add_slider_float(label="Float", default_value=0.5, min_value=0, max_value=1)
        self.__exit__()

class Window(Container):
    @metsig(dpg.window)
    def __init__(self, id: Union[str,int] = 0, *args, **kwargs):
        super().__init__(id=id, *args, **kwargs)

    def describe(self):
        if type(self) is Window:
            raise NotImplementedError("Window is an abstract class")

    def _add(self) -> Union[str,int]:
        super()._add()
        return dpg.add_window(id=self.id, *self.args, **self.kwargs)

    def update(self):
        if type(self) is Window:
            raise NotImplementedError("Window is an abstract class")

class ChildWindow(Container):
    @metsig(dpg.add_child_window)
    def __init__(self, id: Union[str,int] = 0, *args, **kwargs):
        super().__init__(id=id, *args, **kwargs)
        
    def describe(self):
        if type(self) is ChildWindow:
            raise NotImplementedError("ChildWindow is an abstract class")

    def _add(self) -> Union[str,int]:
        super()._add()
        return dpg.add_child_window(id=self.id, *self.args, **self.kwargs)

class HorizontalGroup(Group):
    def __init__(self, id: Union[str,int] = 0, *args, **kwargs):
        super().__init__(id=id, horizontal=True, *args, **kwargs)