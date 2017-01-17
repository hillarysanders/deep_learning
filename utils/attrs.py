from collections import MutableMapping
from premise.richdict import richdict


class attrs(MutableMapping):
    'Mapping objects that also expose an attr interface'

    def __init__(self, *args, **kw):
        self._set(dict(*args, **kw))

    def _set(self, d):
        self.__dict__['_d'] = d

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, k):
        return self._d[k]

    def __setitem__(self, k, v):
        self._d[k] = v

    def __delitem__(self, k):
        del self._d[k]

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return repr(self._d)

    # Map attrs to keys

    def __hasattr__(self, k):
        return k in self

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            # Map dict KeyError to attr AttributeError (e.g. copy.deepcopy breaks without this)
            raise AttributeError(k)

    def __setattr__(self, k, v):
        self[k] = v

    def __delattr__(self, k):
        try:
            del self[k]
        except KeyError:
            # Map dict KeyError to attr AttributeError (e.g. copy.deepcopy breaks without this)
            raise AttributeError(k)

    # Pickling

    def __getstate__(self):
        return self._d

    def __setstate__(self, state):
        self.__dict__['_d'] = state

    # Other attrs methods

    @classmethod
    def wrap_dict(cls, d):
        'Wrap a mapping object without converting it to a standard dict'
        r = cls()
        r._set(d)
        return r

      # Extra behaviors that dict doesn't have (but should)

    def __add__(self, d):
        'Append two dicts (without mutation)'
        return self.wrap_dict(richdict(self._d) + d)

if __name__ == '__main__':
    # TODO Unit tests

    d = attrs(a=1, b=2)
    print d, d.a, d.b
    print dict(**d)

    print

    from latedict import latedict
    d = attrs.wrap_dict(latedict(a=1, b=2))
    print d
    print d.a
    print d.b
    print dict(**d)

    print

    from latedict import latedict
    d = attrs.wrap_dict(latedict(a=1, b=lambda a: a + 1))
    print d, d.a, d.b
    d.a = 10
    print d, d.a, d.b
    d.b = -1
    print d, d.a, d.b
    d.a = 1
    print d, d.a, d.b
    d.b = lambda a: a - 1
    print d, d.a, d.b
