from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Generic, Type, TypeVar, Union, NamedTuple
from typing_extensions import Self
from utils.logger import LOGGER

import dearpygui.dearpygui as dpg
from utils.sig import metsig


class ElementParams():
    def __init__(self, *args, **kwargs):
        '''
            In subclass, please use super().__init__(*args, **kwargs) to call the parent class's __init__
            also, use @metsig(dpg.add_*) to copy the signature of the dpg.add_* function
        '''
        self.args = args
        self.kwargs = kwargs

T = TypeVar('T', bound=ElementParams)
class Element(Generic[T], metaclass=ABCMeta):
    def __init__(self, tag: Union[str, int] = 0):
        self._tag = tag

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def value(self):
        return dpg.get_value(self.tag)

    @abstractmethod
    def _add(self, params: T = None) -> int:
        pass

    def add(self, params: T = None) -> int:
        if params is None: 
            params = ElementParams()
        self.tag = self._add(params)