from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)  #@ReservedAssignment


def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>>
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """

    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


def pymote_equal_objects(obj1, obj2):
    """
    Compare two objects and their attributes, but allow for non immutable
    attributes to be aqual up to their class.
    """
    classes = obj1.__class__ == obj2.__class__
    attr_names = attr_values = True
    if isinstance(obj1, object) and isinstance(obj2, object):
        attr_names = set(obj1.__dict__.keys()) == set(obj2.__dict__.keys())
    types = (str, tuple, int, long, bool, float, frozenset, bytes, complex)
    for key, value in obj1.__dict__.items():
        other_value = getattr(obj2, key, None)
        if (isinstance(value, types) and value!=other_value) or \
            value.__class__!=other_value.__class__:
            attr_values = False
            break
    return classes and attr_names and attr_values
