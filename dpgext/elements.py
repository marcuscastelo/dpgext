from typing import Any, Callable, Dict, Union
from utils.logger import LOGGER
import dpgext.gui as gui
from utils.sig import metsig

import dearpygui.dearpygui as dpg

class Element:
    def __init__(self, id: Union[str, int] = None):
        self._id = id
    
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if self._id == value:
            return

        self._id = value

    @property
    def value(self):
        return dpg.get_value(self.id)

    def construct(self, *args, **kwargs):
        if type(self) == Element:
            LOGGER.log_error("construct() not implemented, Element is an abstract class")
            raise NotImplementedError()

class Button(Element):
    def __init__(self, id: Union[str, int] = None):
        super().__init__(id)

    @metsig(dpg.add_button)
    def construct(self, *args, **kwargs):
        super().construct(*args, **kwargs)
        callback = kwargs.get('callback', None)

        if callback is None:
            LOGGER.log_warning("No callback function specified for button")
            callback = lambda: None
        if self.id is not None:
            self.id = dpg.add_button(id=self.id, *args, **kwargs)
        else:
            self.id = dpg.add_button(*args, **kwargs)

class UpdatableElement(Element):
    updatable_elements_registry: Dict[Union[str, int], 'UpdatableElement'] = {}
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = None):
        super().__init__(id)
        self.object = object
        self.attribute = attribute
        self.pending_reconfigure = False
        assert not id or not self.__class__.updatable_elements_registry.get(id)
        assert hasattr(object, attribute), f"{object=} has no attribute {attribute=}"

    @Element.id.getter
    def id(self):
        return super(UpdatableElement, type(self)).id.fget(self)

    @Element.id.setter # type: ignore
    def id(self, value):
        super(UpdatableElement, type(self)).id.fset(self, value)

        if self._id:
            self.__class__.updatable_elements_registry.pop(self._id, None)
        self._id = value
        self.__class__.updatable_elements_registry[value] = self

    def __del__(self):
        self.__class__.updatable_elements_registry.pop(self._id, None)

    def _combine_callbacks(self, *callbacks) -> Callable:
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

    def construct(self, *args, **kwargs):
        super().construct(*args, **kwargs)

        # Store provided callback as a user-provided callback (we are already using callbacks to update the element's object)
        user_callback = kwargs.get("callback", None)
        self.user_callback = user_callback
        kwargs.pop("callback", None) # Remove the user-provided callback from the kwargs
        # Child classes should create a callback with _combine_callbacks(update_object_callback, user_callback)

        if type(self) == UpdatableElement:
            LOGGER.log_error("construct() not implemented, UpdatableElement is an abstract class")
            raise NotImplementedError("construct() not implemented, UpdatableElement is an abstract class")

    def _reconfigure(self):
        if type(self) == UpdatableElement:
            LOGGER.log_error("_reconfigure() not implemented, UpdatableElement is an abstract class")
            raise NotImplementedError("_reconfigure() not implemented, UpdatableElement is an abstract class")

    def update(self, *args, **kwargs):
        assert gui.is_running(), "Base GUI is not running"

        if self.pending_reconfigure:
            LOGGER.log_trace("Pending reconfigure, calling _reconfigure()", "GUI")
            self._reconfigure()
            self.pending_reconfigure = False

        if type(self) == UpdatableElement:
            LOGGER.log_error("update() not implemented, UpdatableElement is an abstract class")
            raise NotImplementedError("update() not implemented, UpdatableElement is an abstract class")
    
    @classmethod
    def update_all(cls):
        assert gui.is_running(), "Base GUI is not running"
        for element in cls.updatable_elements_registry.values():
            if element.id is not None and dpg.does_item_exist(element.id) and dpg.is_item_visible(element.id):
                element.update()

class Checkbox(UpdatableElement):
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = None):
        super().__init__(object, attribute, id=id)
        self.default_value: bool = getattr(self.object, self.attribute)

        if self.default_value is None:
            self.default_value = False
            
        assert self.default_value in [True, False]

    def _toggle(self) -> None:
        old_value = getattr(self.object, self.attribute)
        setattr(self.object, self.attribute, not old_value)
        pass
    
    @metsig(dpg.add_checkbox)
    def construct(self, *args, **kwargs):
        super().construct(*args, **kwargs) # Creates self.user_callback
        callback = self._combine_callbacks(self._toggle, self.user_callback)
        kwargs["callback"] = callback # Override callback with our own
        
        if self.id is not None:
            self.id = dpg.add_checkbox(id=self.id, default_value=self.default_value, *args, **kwargs)
        else:
            self.id = dpg.add_checkbox(default_value=self.default_value, *args, **kwargs)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.id is not None:
            dpg.set_value(item=self.id, value=getattr(self.object, self.attribute))


class Slider(UpdatableElement):
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = None):
        super().__init__(object, attribute, id)
        self.attribute_type = type(getattr(self.object, self.attribute))
        
        constructors = {
            float: dpg.add_slider_float,
            int: dpg.add_slider_int,
        }

        if self.attribute_type not in constructors:
            LOGGER.log_error(f"Unsupported attribute type {self.attribute_type=}")
            raise NotImplementedError(f"Unsupported attribute type {self.attribute_type=}")

        self.constructor = constructors.get(self.attribute_type)

    def _set_value(self, _ = None, value = None) -> None:
        value = dpg.get_value(item=self.id)
        setattr(self.object, self.attribute, value)

    @metsig(dpg.add_slider_float)
    def construct(self, *args, **kwargs):
        super().construct(*args, **kwargs) # Creates self.user_callback
        callback = self._combine_callbacks(self._set_value, self.user_callback)
        kwargs["callback"] = callback # Override callback with our own
        if kwargs.get("default_value", None) is None:
            kwargs["default_value"] = getattr(self.object, self.attribute)
        if self.id is not None:
            self.id = self.constructor(id=self.id, *args, **kwargs)
        else:
            self.id = self.constructor(*args, **kwargs)

class Text(Element):
    def __init__(self, text: str = '', id: Union[str, int] = None):
        super().__init__(id)
        self.default_text = text

    def construct(self, *args, **kwargs):
        super().construct(*args, **kwargs)

        if self.id is not None:
            self.id = dpg.add_text(id=self.id, default_value=self.default_text, *args, **kwargs)
        else:
            self.id = dpg.add_text(default_value=self.default_text, *args, **kwargs)

class LabeledSlider(Slider):
    def __init__(self, object: Any, attribute: str, label_text: str, label_same_line=True, id: Union[str, int] = None):
        super().__init__(object, attribute, id)
        self.label_text = label_text
        self.label_same_line = label_same_line

    def _add_label_and_slider(self, *args, **kwargs):
        dpg.add_text(self.label_text)
        super().construct(*args, **kwargs)

    @metsig(dpg.add_slider_float)
    def construct(self, *args, **kwargs):
        if self.label_same_line:
            with dpg.group(horizontal=True):
                self._add_label_and_slider(*args, **kwargs)
        else:
            self._add_label_and_slider(*args, **kwargs)

    # test = metsig(dpg.add_slider_float)(_construct)

class InputText(UpdatableElement):
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = None):
        super().__init__(object, attribute, id=id)
        self.default_value: str = getattr(self.object, self.attribute)
        if self.default_value is None:
            self.default_value = ""
        
        assert isinstance(self.default_value, str)

    def _set_value(self, _ = None, value = None) -> None:
        value = dpg.get_value(item=self.id)
        setattr(self.object, self.attribute, value)

    @metsig(dpg.add_input_text)
    def construct(self, *args, **kwargs):
        super().construct(*args, **kwargs)

        if self.user_callback is not None:
            callback = self._combine_callbacks(self._set_value, self.user_callback)
            kwargs["callback"] = callback

        kwargs["default_value"] = self.default_value
        if self.id is not None:
            self.id = dpg.add_input_text(id=self.id, *args, **kwargs)
        else:
            self.id = dpg.add_input_text(*args, **kwargs)
        
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.id is not None:
            dpg.set_value(item=self.id, value=getattr(self.object, self.attribute))


class ComboBox(UpdatableElement):
    def __init__(self, object: Any, attribute: str, items: list, id: Union[str, int] = None):
        super().__init__(object, attribute, id)
        self.default_value: str = getattr(self.object, self.attribute)
        if self.default_value is None:
            self.default_value = ""

        if not isinstance(items, list):
            raise TypeError("items must be a list")

        self.items = items
        assert self.default_value in self.items, f"{self.default_value=} is not in {self.items=}"

        self.require_reconfigure = False

    def _set_value(self, _ = None, value = None) -> None:
        value = dpg.get_value(item=self.id)
        setattr(self.object, self.attribute, value)

    def _warn_filter_kwargs(self, **kwargs) -> dict[str, Any]:
        if "default_value" in kwargs:
            LOGGER.log_error("'default_value' is internally set by the ComboBox") #TODO: propagate to other classes
            del kwargs["default_value"]

        if 'items' in kwargs:
            LOGGER.log_error("'items' is internally set by the ComboBox, use 'set_items' instead") #TODO: propagate to other classes
            del kwargs["items"]

        return kwargs

    @metsig(dpg.add_combo)
    def construct(self, *args, **kwargs):
        super().construct(*args, **kwargs)
        kwargs = self._warn_filter_kwargs(**kwargs) #TODO: propagate to other classes

        if self.user_callback is not None:
            callback = self._combine_callbacks(self._set_value, self.user_callback)
            kwargs["callback"] = callback

        kwargs["default_value"] = self.default_value
        kwargs["items"] = self.items
        if self.id is not None:
            self.id = dpg.add_combo(id=self.id, *args, **kwargs)
        else:
            self.id = dpg.add_combo(*args, **kwargs)

    def _reconfigure(self):
        super()._reconfigure()
        LOGGER.log_trace("Reconfiguring ComboBox", 'GUI.ComboBox')
        dpg.configure_item(self.id, items=self.items)

    def set_items(self, items: list):
        self.items = items
        self.require_reconfigure = True

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.require_reconfigure:
            self._reconfigure()
            self.require_reconfigure = False