from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Dict, Union
from dpgext.elements.element import Element, T, ElementParams
from utils.logger import LOGGER

import dearpygui.dearpygui as dpg


def _combine_callbacks(*callbacks: Callable) -> Callable:
        def callback(*args, **kwargs):
            for callback in callbacks:
                if callback is None:
                    # LOGGER.log_warning("Ignoring callback function that is None", 'GUI')
                    continue
                
                if callable(callback):
                    callback(*args, **kwargs)
                else:
                    LOGGER.log_error(f"{callback=} is not callable")
        return callback

class UpdatableElement(Element[T], metaclass=ABCMeta):
    updatable_elements_registry: Dict[Union[str, int], 'UpdatableElement'] = {}
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = None):
        super().__init__(id)
        self.object = object
        self.attribute = attribute
        self._pending_reconfigure = False
        assert not id or not self.__class__.updatable_elements_registry.get(id)
        assert hasattr(object, attribute), f"{object=} has no attribute {attribute=}"

    def __del__(self):
        self.__class__.updatable_elements_registry.pop(self._tag, None)

    @Element.tag.getter
    def tag(self):
        return super(UpdatableElement, type(self)).tag.fget(self)

    @Element.tag.setter # type: ignore
    def tag(self, value):
        super(UpdatableElement, type(self)).tag.fset(self, value)

        if self._tag:
            self.__class__.updatable_elements_registry.pop(self._tag, None)
        self._tag = value
        self.__class__.updatable_elements_registry[value] = self

    @abstractmethod
    def _set_value(self, tag: int, value): ...

    def add(self, params: T = None):
        if params is None:
            params = ElementParams()

        # Before adding, combine the user callback with the _set_value callback
        user_callback = params.kwargs.get("callback", None)
        self.user_callback = user_callback

        callback = self._set_value
        if user_callback is not None:
            callback = _combine_callbacks(callback, user_callback)

        params.kwargs["callback"] = callback


        # Add the element
        super().add(params)

    @abstractmethod
    def _reconfigure(self): ...

    def update(self, *args, **kwargs):
        if self._pending_reconfigure:
            LOGGER.log_trace("Pending reconfigure, calling _reconfigure()", "GUI")
            self._reconfigure()
            self._pending_reconfigure = False

        if type(self) == UpdatableElement:
            LOGGER.log_error("update() not implemented, UpdatableElement is an abstract class")
            raise NotImplementedError("update() not implemented, UpdatableElement is an abstract class")
    
    @classmethod
    def update_all(cls):
        for element in cls.updatable_elements_registry.values():
            if element.tag is not None and dpg.does_item_exist(element.tag) and dpg.is_item_visible(element.tag):
                element.update()
