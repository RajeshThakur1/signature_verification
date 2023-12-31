from abc import ABCMeta


class SyneSingleton(ABCMeta):
    """This is a singleton metaclass for implementing singletone interfaces.
    author:rajesh
    Args:
        ABCMeta (_type_): _description_
    Returns:
        _type_: _description_
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SyneSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
