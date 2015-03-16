#!/usr/bin/env python
"""
This module provides decorator of input param check for functions
"""

def required(**types):
    """
    Parameters constrainted by required must be an instance of types specified and not none.
    :param types: param and types
    :return: decorated function
    """
    def _required(f):
        def _decorated(*args, **kwds):
            for i, v in enumerate(args):
                if f.func_code.co_varnames[i] in types:
                    if v is None:
                        raise ValueError('arg "%s" should not be None' %
                                         (f.func_code.co_varnames[i]))
                    if not isinstance(v, types[f.func_code.co_varnames[i]]):
                        raise TypeError('arg "%s"= %r does not match %s' %
                                        (f.func_code.co_varnames[i],
                                         v,
                                         types[f.func_code.co_varnames[i]]))
            for k, v in kwds.iteritems():
                if k in types:
                    if v is None:
                        raise ValueError('arg "%s" should not be None' % k)
                    if not isinstance(v, types[k]):
                        raise TypeError('arg "%s"= %r does not match %s' % (k, v, types[k]))
            return f(*args, **kwds)
        _decorated.func_name = f.func_name
        return _decorated
    return _required


# examples are here
if __name__ == "__main__":
    # decorated function
    @required(str_param=(str, unicode), num_param=(int, long))
    def test_func(str_param, num_param, ok=None):
        print str_param, num_param, ok
    # call function with wrong type
    try:
        test_func(123, 456)
    except TypeError as e:
        print e
    # call function with wrong value
    try:
        test_func("123", None)
    except ValueError as e:
        print e