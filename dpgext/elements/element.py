import abc
from typing import TypeVar, Union
from utils.logger import LOGGER

import dearpygui.dearpygui as dpg
from utils.sig import metsig

class ElementParameters:
    @metsig(dpg.add_button)
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

T = TypeVar('T')
class Element(metaclass=abc.ABCMeta):
    def __init__(self, tag: Union[str, int] = 0):
        self._tag = tag
    
    # Getters and setters 
    # (default is just plain getters and setters, 
    # but can be overridden)

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def value(self):
        return dpg.get_value(self.tag)

    @metsig(T)
    def add(self, *args, **kwargs):
        self.tag = self._add(*args, **kwargs)

    @abc.abstractmethod
    @metsig(T)
    def _add(self, *args, **kwargs) -> int:
        pass
