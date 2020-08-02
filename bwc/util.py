import inspect
import re
from os.path import abspath, dirname, join
from random import choice
from typing import List

# Root directory of the module
MODULE_ROOT = dirname(abspath(__file__))


class MetaFactory(type):
    def __new__(mcs, name, bases, attrs):
        # There will _always_ only be one base class - the proxied object's class.
        base = bases[0]
        # These are the attributes from Proxy() that we want to have override the parent class.
        whitelist = ['__new__', '__getattr__', '__getattribute__', '__setattr__', '__getitem__', '__setitem__',
                     '__repr__', '__str__', '__init__']
        for attr, val in inspect.getmembers(base):
            if attr not in whitelist:
                if not hasattr(val, '__call__'):
                    # Normal, non-callable attributes can just be proxied as-is.
                    # print(f'Normal-proxying attr {attr}')
                    attrs[attr] = val
                else:
                    # Callables require a bit more work - in the case of builtins, they _require_ that
                    # the actual backing object be passed as the first argument (? maybe not?  But that seems to fix the errors so idk)
                    # print(f"Call-proxying attr {attr}")

                    def proxy_wrapper(attr_name):
                        # We need the outer proxy_wrapper to make sure the value of attr_name gets preserved in the closure.
                        def mproxy(self, *args, **kwargs):
                            if isinstance(type(self), MetaFactory):
                                # print(f"PROXYING {attr_name}")
                                return immutablize(
                                    getattr(base, attr_name)(self._backing_obj, *args, **kwargs))
                            else:
                                # print(f"SUPER TRANSPARENT PROXYING {self} {attr_name}")
                                # print(f'{args}')
                                return immutablize(getattr(base, attr_name)(self, *args, **kwargs))

                        return mproxy

                    attrs[attr] = proxy_wrapper(attr)
        name = base.__name__
        return super(MetaFactory, mcs).__new__(mcs, name, bases, attrs)

    def __getattribute__(cls, attr):
        # print(f'mcls {attr}')
        return super().__getattribute__(attr)


# id(type(target)) => Optional[Proxy class]
# if proxy class is None, then it can't be immutablized
_cls_cache = {}


def immutablize(target):
    """
    Given a target object, return an immutable proxy around it.
    Any attempts to set attributes on the returned object will
    raise an AttributeError with a descriptive error message.
    The original, mutable object can be accessed at ._backing_obj
    if necessary.
    """
    if target is None:
        return None
    if type(type(target)).__name__ == 'MetaFactory':  # it's already immutable
        return target

    i = id(type(target))
    if i in _cls_cache:
        if _cls_cache[i] is not None:
            return _cls_cache[i](target)
        else:
            return target

    try:
        class Proxy(type(target), metaclass=MetaFactory):
            def __init__(self, obj):
                # print("YEET PROXY INIT")
                object.__setattr__(self, "_backing_obj", obj)

            def __getattr__(self, attr):
                # print(f"cls {attr}")
                backing = object.__getattribute__(self, "_backing_obj")
                if attr == "_backing_obj":
                    return backing
                return immutablize(getattr(backing, attr))

            def __setattr__(self, attr, val):
                raise AttributeError("Error: Card attempted to change gamestate without kernel call!")

            def __getitem__(self, attr):
                return immutablize(self._backing_obj[attr])

            def __setitem__(self, attr, val):
                raise AttributeError("Error: Card attempted to manipulate state without kernel call!")

            def __repr__(self):
                return repr(self._backing_obj)

            def __str__(self):
                return str(self._backing_obj)

        out = Proxy(target)
        _cls_cache[i] = Proxy
        return out
    except TypeError:
        # Failed to proxy, probably because the target was an unsubclassable base type
        _cls_cache[i] = None
        return target


def random_id(disallowed: List[str] = None) -> str:
    if disallowed is None:
        disallowed = []
    with open(join(MODULE_ROOT, 'words.txt'), 'r') as f:
        while True:
            c = choice(f.read().strip().split('\n'))
            if c not in disallowed:
                return c


# Explanation: lowercase letters are the easiest to type quickly
VALID_NAME_REGEX = re.compile(r"^[a-z]+$")
# Explanation: rooms should have 0 chance of doing anything weird in html
# so, only allow letters, numbers, and single dashes in between
VALID_ROOM_REGEX = re.compile(r"^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$")


def is_valid_player_name(player_name: str) -> bool:
    return bool(VALID_NAME_REGEX.fullmatch(player_name))


def is_valid_room_name(room_name: str) -> bool:
    return bool(VALID_ROOM_REGEX.fullmatch(room_name))
