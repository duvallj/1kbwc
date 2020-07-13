from random import choice

def immutablize(target):
    if target is None:
        return None
    class MetaFactory(type):
        def __new__(mcls, name, bases, attrs):
            whitelist = ['__getattr__', '__setattr__', '__getitem__', '__setitem__', '__repr__', '__str__', '__init__']
            for attr in dir(type(target)):
                if attr not in whitelist:
                    attrs[attr] = getattr(type(target), attr)
            name = type(target).__name__
            bases += (type(target),)
            return super(MetaFactory, mcls).__new__(mcls, name, bases, attrs)
        
    class Proxy(metaclass=MetaFactory):
        def __init__(self, obj):
            object.__setattr__(self, "_backing_obj", obj)
        def __getattr__(self, attr):
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
    
    return Proxy(target)

def random_id(disallowed=[]):
    with open('words.txt', 'r') as f:
        while(True):
            c = choice(f.read().strip().split('\n'))
            if c not in disallowed:
                return c
    return 'THIS_ID'
