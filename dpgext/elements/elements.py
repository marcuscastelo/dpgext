from typing import Any, Callable, Dict, Union
from dpgext.elements.element import Element, ElementParams
from dpgext.elements.updatable_element import UpdatableElement
from utils.logger import LOGGER
import dpgext.gui as gui
from utils.sig import metsig

import dearpygui.dearpygui as dpg

class ButtonParams(ElementParams):
    @metsig(dpg.add_button)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Button(Element[ButtonParams]):
    def __init__(self, id: Union[str, int] = 0):
        super().__init__(id)

    @metsig(dpg.add_button)
    def _add(self, params: ButtonParams) -> int:
        callback = params.kwargs.get('callback', None)
        if callback is None:
            LOGGER.log_warning("No callback function specified for button")
            callback = lambda: None
        params.kwargs['callback'] = callback

        return dpg.add_button(*params.args, **params.kwargs, tag=self._tag)

class CheckboxParams(ElementParams):
    @metsig(dpg.add_checkbox)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CheckBox(UpdatableElement[CheckboxParams]):
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = 0):
        super().__init__(object, attribute, id=id)
        self.default_value: bool = getattr(self.object, self.attribute)

        if self.default_value is None:
            self.default_value = False
            
        assert self.default_value in [True, False]

    def _set_value(self, _, _value: bool):
        old_value = getattr(self.object, self.attribute)
        setattr(self.object, self.attribute, not old_value)

    @metsig(dpg.add_checkbox)
    def _add(self, params: CheckboxParams) -> int:
        return dpg.add_checkbox(default_value=self.default_value, *params.args, **params.kwargs, tag=self.tag)

    def update(self, *args, **kwargs):
        dpg.set_value(item=self.tag, value=getattr(self.object, self.attribute))

    def _reconfigure(self):
        pass

class SliderFloatParams(ElementParams):
    @metsig(dpg.add_slider_float)
    def _add(self, *args, **kwargs) -> int:
        return dpg.add_slider(*args, **kwargs, tag=self._tag)

class SliderFloat(UpdatableElement[SliderFloatParams]):
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = 0):
        super().__init__(object, attribute, id=id)
        self.default_value: float = getattr(self.object, self.attribute)

        if self.default_value is None:
            self.default_value = 0.0

    def _set_value(self, _, value: float):
        setattr(self.object, self.attribute, value)

    @metsig(dpg.add_slider_float)
    def _add(self, params: SliderFloatParams) -> int:
        #TODO: change default value to self.default_value if it is None
        return dpg.add_slider_float(default_value=self.default_value, *params.args, **params.kwargs, tag=self.tag)

    def _reconfigure(self):
        pass


class SliderIntParams(ElementParams):
    @metsig(dpg.add_slider_int)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SliderInt(UpdatableElement[SliderIntParams]):
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = 0):
        super().__init__(object, attribute, id=id)
        self.default_value: int = getattr(self.object, self.attribute)

        if self.default_value is None:
            self.default_value = 0

    def _set_value(self, _, value: int):
        setattr(self.object, self.attribute, value)

    @metsig(dpg.add_slider_int)
    def _add(self, params: SliderIntParams) -> int:
        #TODO: change default value to self.default_value if it is None
        return dpg.add_slider_int(default_value=self.default_value, *params.args, **params.kwargs, tag=self.tag)

class TextParams(ElementParams):
    @metsig(dpg.add_text)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Text(Element[TextParams]):
    @metsig(dpg.add_text)
    def _add(self, params: TextParams) -> int:
        # TODO: warn_filter
        # kwargs['default_value'] = self.default_text
        return dpg.add_text(*params.args, **params.kwargs, tag=self.tag)

class InputTextParams(ElementParams):
    @metsig(dpg.add_input_text)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class InputText(UpdatableElement[InputTextParams]):
    def __init__(self, object: Any, attribute: str, id: Union[str, int] = 0):
        super().__init__(object, attribute, id=id)
        self.default_value: str = getattr(self.object, self.attribute)
        if self.default_value is None:
            self.default_value = ""
        
        assert isinstance(self.default_value, str)

    def _set_value(self, _ = None, value = None) -> None:
        value = dpg.get_value(item=self.tag)
        setattr(self.object, self.attribute, value)

    def _reconfigure(self):
        # TODO: implement
        pass

    @metsig(dpg.add_input_text)
    def _add(self, params: InputTextParams) -> int:
        params.kwargs["default_value"] = self.default_value
        return dpg.add_input_text(id=self.tag, *params.args, **params.kwargs, tag=self.tag)
        
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.tag is not None:
            dpg.set_value(item=self.tag, value=getattr(self.object, self.attribute))

class ComboParams(ElementParams):
    @metsig(dpg.add_combo)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Combo(UpdatableElement[ComboParams]):
    def __init__(self, object: Any, attribute: str, items: list, id: Union[str, int] = 0):
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
        value = dpg.get_value(item=self.tag)
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
    def _add(self, params: ComboParams) -> int:
        params.kwargs = self._warn_filter_kwargs(**params.kwargs) #TODO: propagate to other classes
        params.kwargs["default_value"] = self.default_value
        params.kwargs["items"] = self.items

        return dpg.add_combo(*params.args, **params.kwargs, tag=self.tag)

    def _reconfigure(self):
        super()._reconfigure()
        LOGGER.log_trace("Reconfiguring ComboBox", 'GUI.ComboBox')
        dpg.configure_item(self.tag, items=self.items)

    def set_items(self, items: list):
        self.items = items
        self.require_reconfigure = True

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        if self.require_reconfigure:
            self._reconfigure()
            self.require_reconfigure = False