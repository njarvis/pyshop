import sys
import collections
import functools
import inspect


class memoized(object):
    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)


def log_fn(write=sys.stdout.write, log=None):
    """ Log calls to a function.

    Returns a decorated version of the input function which "echoes" calls
    made to it by writing out the function's name and the arguments it was
    called with.
    """

    def wrap(fn):
        import functools

        def name(item):
            """ Return an item's name. """
            return item.__name__

        def format_arg_value(arg_val):
            """ Return a string representing a (name, value) pair.

            >>> format_arg_value(('x', (1, 2, 3)))
            'x=(1, 2, 3)'
            """
            arg, val = arg_val
            return "%s=%r" % (arg, val)

        def output(s):
            if log is not None:
                log(s)
            elif write is not None:
                write(s + '\n')

        # Unpack function's arg count, arg names, arg defaults
        code = fn.func_code
        argcount = code.co_argcount
        argnames = code.co_varnames[:argcount]
        fn_defaults = fn.func_defaults or list()
        argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

        @functools.wraps(fn)
        def wrapped_f(*v, **k):
            # Collect function arguments by chaining together positional,
            # defaulted, extra positional and keyword arguments.
            positional = map(format_arg_value, zip(argnames, v))
            defaulted = [format_arg_value((a, argdefs[a]))
                         for a in argnames[len(v):] if a not in k]
            nameless = map(repr, v[argcount:])
            keyword = map(format_arg_value, k.items())
            args = positional + defaulted + nameless + keyword

            output("%% Entering {fn}({args})".format(fn=name(fn), args=", ".join(args)))
            try:
                result = fn(*v, **k)
            except Exception as e:
                output("%% Exiting {fn} with exception '{exception}'".format(fn=name(fn), exception=e))
                raise
            else:
                output("%% Exiting {fn}, returning {result}".format(fn=name(fn), result=repr(result)))
                return result

        return wrapped_f
    return wrap


def echo(fn, write=sys.stdout.write, log=None):
    """ Echo calls to a function.

    Returns a decorated version of the input function which "echoes" calls
    made to it by writing out the function's name and the arguments it was
    called with.
    """

    if not hasattr(echo, "depth"):
        echo.depth = 1  # it doesn't exist yet, so initialize it

    def name(item):
        """ Return an item's name. """
        return item.__name__

    def format_arg_value(arg_val):
        """ Return a string representing a (name, value) pair.

        >>> format_arg_value(('x', (1, 2, 3)))
        'x=(1, 2, 3)'
        """
        arg, val = arg_val
        return "%s=%r" % (arg, val)

    def output(s, indent='>'):
        if log is not None:
            log(indent * echo.depth + ' ' + s)
        elif write is not None:
            write(indent * echo.depth + ' ' + s + '\n')

    import functools
    # Unpack function's arg count, arg names, arg defaults
    code = fn.func_code
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.func_defaults or list()
    argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

    @functools.wraps(fn)
    def wrapped(*v, **k):
        # Collect function arguments by chaining together positional,
        # defaulted, extra positional and keyword arguments.
        positional = map(format_arg_value, zip(argnames, v))
        defaulted = [format_arg_value((a, argdefs[a]))
                     for a in argnames[len(v):] if a not in k]
        nameless = map(repr, v[argcount:])
        keyword = map(format_arg_value, k.items())
        args = positional + defaulted + nameless + keyword
        output("Entering {fn}({args})".format(fn=name(fn), args=", ".join(args)), '>')
        try:
            echo.depth += 1
            result = fn(*v, **k)
        except Exception as e:
            echo.depth -= 1
            output("Exiting {fn} with exception '{exception}'".format(fn=name(fn), exception=e), '<')
            raise
        else:
            echo.depth -= 1
            output("Exiting {fn}, returning {result}".format(fn=name(fn), result=repr(result)), '<')
            return result
    return wrapped


def echo_instancemethod(klass, method, write=sys.stdout.write):
    """ Change an instancemethod so that calls to it are echoed.

    Replacing a classmethod is a little more tricky.
    See: http://www.python.org/doc/current/ref/types.html
    """

    def name(item):
        """ Return an item's name. """
        return item.__name__

    def is_classmethod(instancemethod):
        " Determine if an instancemethod is a classmethod. "
        return instancemethod.im_self is not None

    def is_class_private_name(name):
        " Determine if a name is a class private name. "
        # Exclude system defined names such as __init__, __add__ etc
        return name.startswith("__") and not name.endswith("__")

    def method_name(method):
        """ Return a method's name.

        This function returns the name the method is accessed by from
        outside the class (i.e. it prefixes "private" methods appropriately).
        """
        mname = name(method)
        if is_class_private_name(mname):
            mname = "_%s%s" % (name(method.im_class), mname)
        return mname

    mname = method_name(method)
    never_echo = "__str__", "__repr__",  # Avoid recursion printing method calls
    if mname in never_echo:
        pass
    elif is_classmethod(method):
        setattr(klass, mname, classmethod(echo(method.im_func, write)))
    else:
        setattr(klass, mname, echo(method, write))


def echo_class(klass, write=sys.stdout.write):
    """ Echo calls to class methods and static functions
    """
    def name(item):
        """ Return an item's name. """
        return item.__name__

    for _, method in inspect.getmembers(klass, inspect.ismethod):
        echo_instancemethod(klass, method, write)
    for _, fn in inspect.getmembers(klass, inspect.isfunction):
        setattr(klass, name(fn), staticmethod(echo(fn, write)))


def echo_module(mod, write=sys.stdout.write):
    """ Echo calls to functions and methods in a module.
    """
    for fname, fn in inspect.getmembers(mod, inspect.isfunction):
        setattr(mod, fname, echo(fn, write))
    for _, klass in inspect.getmembers(mod, inspect.isclass):
        echo_class(klass, write)


def accepts(**types):
    def check_accepts(f):
        @functools.wraps(f)
        def new_f(*args, **kwds):
            for i, v in enumerate(args):
                if f.func_code.co_varnames[i] is not 'self' and \
                   types in f.func_code.co_varnames[i] and \
                   types[f.func_code.co_varnames[i]] and \
                   not isinstance(v, types[f.func_code.co_varnames[i]]):
                    raise TypeError("arg '%s'=%r does not match %s" %
                                    (f.func_code.co_varnames[i], v, types[f.func_code.co_varnames[i]]))
                    del types[f.func_code.co_varnames[i]]

            for k, v in kwds.iteritems():
                if types in k and not isinstance(v, types[k]):
                    raise TypeError("arg '%s'=%r does not match %s" % (k, v, types[k]))

            return f(*args, **kwds)
        return new_f
    return check_accepts

if __name__ == "__main__":
    import logging
    logging.basicConfig()

    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.INFO)

    @log_fn()
    def a(*args, **kwargs):
        return args, kwargs

    @log_fn(write=None)
    def b():
        pass

    @log_fn(log=LOGGER.info)
    def c(raiseException=False):
        if raiseException:
            raise Exception('I take exception')
        else:
            return raiseException

    a()
    a(1)
    a(1, testing=True)

    b()

    c()
    try:
        c(True)
    except:
        pass
