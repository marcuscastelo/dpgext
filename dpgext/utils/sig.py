
import inspect
from typing import Any, Callable, TypeVar, Protocol
from typing_extensions import ParamSpec, Concatenate

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T')

def funcsig(target: Callable[P, R]) -> Callable[...,Callable[P, R]]:
    def inner(wrapper: Callable[..., Any]) -> Callable[P, R]:
        if inspect.ismethod(wrapper):
            wrapper = wrapper.__func__
        return wrapper
    return inner


def metsig(target: Callable[P, R]) -> Callable[..., Callable[Concatenate[T, P], R]]:
    def inner(wrapper: Callable[..., Any]) -> Callable[Concatenate[T, P], R]:
        if inspect.ismethod(wrapper):
            wrapper = wrapper.__func__
        return wrapper
    return inner