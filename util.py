def immutablize(target):
    if target is None:
        return None
    class MetaFactory(type):
        def __new__(mcls, name, bases, attrs):
            whitelist = ['__getattribute__', '__setattr__', '__init__']
            for attr in dir(type(target)):
                if attr not in whitelist:
                    attrs[attr] = getattr(type(target), attr)
            name = type(target).__name__
            bases += (type(target),)
            return super(MetaFactory, mcls).__new__(mcls, name, bases, attrs)
        
    class Proxy(metaclass=MetaFactory):
        def __init__(self, obj):
            object.__setattr__(self, "_backing_obj", obj)
        def __getattribute__(self, attr):
            ret = getattr(object.__getattribute__(self, "_backing_obj"), attr)
            return immutablize(ret)
        def __setattr__(self, attr, val):
            raise AttributeError("Err: Card attempted to change gamestate without kernel call")
    
    return Proxy(target)
