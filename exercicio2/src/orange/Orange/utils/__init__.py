"""
.. index:: utils

Orange.utils contains developer utilities.

------------------
Reporting progress
------------------

.. autoclass:: Orange.utils.ConsoleProgressBar
    :members:

-----------------------------
Deprecation utility functions
-----------------------------

.. autofunction:: Orange.utils.deprecation_warning

.. autofunction:: Orange.utils.deprecated_members

.. autofunction:: Orange.utils.deprecated_keywords

.. autofunction:: Orange.utils.deprecated_attribute

.. autofunction:: Orange.utils.deprecated_function_name

----------------
Submodules
----------------

.. automodule:: Orange.utils.environ

.. automodule:: Orange.utils.counters
  :members:

.. automodule:: Orange.utils.render
  :members:

.. automodule:: Orange.utils.addons

.. automodule:: Orange.utils.selection

.. automodule:: Orange.utils.serverfiles

"""

__all__ = ["deprecated_members", "deprecated_keywords",
           "deprecated_attribute", "deprecation_warning",
           "deprecated_function_name",
           "counters", "render", "serverfiles"]

import environ

def deprecation_warning(old, new, stacklevel=-2):
    """ Raise a deprecation warning of an obsolete attribute access.
    
    :param old: Old attribute name (used in warning message).
    :param new: New attribute name (used in warning message).
    
    """
    warnings.warn("'%s' is deprecated. Use '%s' instead!" % (old, new), DeprecationWarning, stacklevel=stacklevel)
   
# We need to get the instancemethod type 
class _Foo():
    def bar(self):
        pass
instancemethod = type(_Foo.bar)
del _Foo

function = type(lambda: None)

class universal_set(set):
    """ A universal set, pretends it contains everything.
    """
    def __contains__(self, value):
        return True
    
from functools import wraps

def deprecated_members(name_map, wrap_methods="all", in_place=True):
    """ Decorate a class with properties for accessing attributes, and methods
    with deprecated names. In addition methods from the `wrap_methods` list
    will be wrapped to receive mapped keyword arguments.
    
    :param name_map: A dictionary mapping old into new names.
    :type name_map: dict
    
    :param wrap_methods: A list of method names to wrap. Wrapped methods will
        be called with mapped keyword arguments (by default all methods will
        be wrapped).
    :type wrap_methods: list
    
    :param in_place: If True the class will be modified in place, otherwise
        it will be subclassed (default True).
    :type in_place: bool
    
    Example ::
            
        >>> class A(object):
        ...     def __init__(self, foo_bar="bar"):
        ...         self.set_foo_bar(foo_bar)
        ...     
        ...     def set_foo_bar(self, foo_bar="bar"):
        ...         self.foo_bar = foo_bar
        ...
        ... A = deprecated_members(
        ... {"fooBar": "foo_bar", 
        ...  "setFooBar":"set_foo_bar"},
        ... wrap_methods=["set_foo_bar", "__init__"])(A)
        ... 
        ...
        >>> a = A(fooBar="foo")
        __main__:1: DeprecationWarning: 'fooBar' is deprecated. Use 'foo_bar' instead!
        >>> print a.fooBar, a.foo_bar
        foo foo
        >>> a.setFooBar("FooBar!")
        __main__:1: DeprecationWarning: 'setFooBar' is deprecated. Use 'set_foo_bar' instead!
        
    .. note:: This decorator does nothing if \
        :obj:`Orange.utils.environ.orange_no_deprecated_members` environment \
        variable is set to `True`.
        
    """
    if environ.orange_no_deprecated_members:
        return lambda cls: cls
    
    def is_wrapped(method):
        """ Is member method already wrapped.
        """
        if getattr(method, "_deprecate_members_wrapped", False):
            return True
        elif hasattr(method, "im_func"):
            im_func = method.im_func
            return getattr(im_func, "_deprecate_members_wrapped", False)
        else:
            return False
        
    if wrap_methods == "all":
        wrap_methods = universal_set()
    elif not wrap_methods:
        wrap_methods = set()
        
    def wrapper(cls):
        cls_names = {}
        # Create properties for accessing deprecated members
        for old_name, new_name in name_map.items():
            cls_names[old_name] = deprecated_attribute(old_name, new_name)
            
        # wrap member methods to map keyword arguments
        for key, value in cls.__dict__.items():
            if isinstance(value, (instancemethod, function)) \
                and not is_wrapped(value) and key in wrap_methods:
                
                wrapped = deprecated_keywords(name_map)(value)
                wrapped._deprecate_members_wrapped = True # A flag indicating this function already maps keywords
                cls_names[key] = wrapped
        if in_place:
            for key, val in cls_names.items():
                setattr(cls, key, val)
            return cls
        else:
            return type(cls.__name__, (cls,), cls_names)
        
    return wrapper

def deprecated_keywords(name_map):
    """ Deprecates the keyword arguments of the function.
    
    Example ::
    
        >>> @deprecated_keywords({"myArg": "my_arg"})
        ... def my_func(my_arg=None):
        ...     print my_arg
        ...
        ...
        >>> my_func(myArg="Arg")
        __main__:1: DeprecationWarning: 'myArg' is deprecated. Use 'my_arg' instead!
        Arg
        
    .. note:: This decorator does nothing if \
        :obj:`Orange.utils.environ.orange_no_deprecated_members` environment \
        variable is set to `True`.
        
    """
    if environ.orange_no_deprecated_members:
        return lambda func: func
    for name in name_map.values():
        if name in name_map:
            raise ValueError("Deprecation keys and values overlap; this could"
                             " cause trouble!")
    
    def decorator(func):
        @wraps(func)
        def wrap_call(*args, **kwargs):
            kwargs = dict(kwargs)
            for name in name_map:
                if name in kwargs:
                    deprecation_warning(name, name_map[name], stacklevel=3)
                    kwargs[name_map[name]] = kwargs[name]
                    del kwargs[name]
            return func(*args, **kwargs)
        return wrap_call
    return decorator

def deprecated_attribute(old_name, new_name):
    """ Return a property object that accesses an attribute named `new_name`
    and raises a deprecation warning when doing so.

    ..

        >>> sys.stderr = sys.stdout
    
    Example ::
    
        >>> class A(object):
        ...     def __init__(self):
        ...         self.my_attr = "123"
        ...     myAttr = deprecated_attribute("myAttr", "my_attr")
        ...
        ...
        >>> a = A()
        >>> print a.myAttr
        ...:1: DeprecationWarning: 'myAttr' is deprecated. Use 'my_attr' instead!
        123
        
    .. note:: This decorator does nothing and returns None if \
        :obj:`Orange.utils.environ.orange_no_deprecated_members` environment \
        variable is set to `True`.
        
    """
    if environ.orange_no_deprecated_members:
        return None
    
    def fget(self):
        deprecation_warning(old_name, new_name, stacklevel=3)
        return getattr(self, new_name)
    
    def fset(self, value):
        deprecation_warning(old_name, new_name, stacklevel=3)
        setattr(self, new_name, value)
    
    def fdel(self):
        deprecation_warning(old_name, new_name, stacklevel=3)
        delattr(self, new_name)
    
    prop = property(fget, fset, fdel,
                    doc="A deprecated member '%s'. Use '%s' instead." % (old_name, new_name))
    return prop 

class class_property(object):
    def __init__(self, fget=None, fset=None, fdel=None, doc="class property"):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc
        
    def __get__(self, instance, owner):
        if instance is None:
            return self.fget(owner)
        else:
            return self.fget(instance)                
            
def deprecated_class_attribute(old_name, new_name):
    """ Return a property object that accesses an class attribute
    named `new_name` and raises a deprecation warning when doing so.
    
    """
    if environ.orange_no_deprecated_members:
        return None
    
    def fget(self):
        deprecation_warning(old_name, new_name, stacklevel=3)
        return getattr(self, new_name)
        
    prop = class_property(fget,
                    doc="A deprecated class member '%s'. Use '%s' instead." % (old_name, new_name))
    return prop

def deprecated_function_name(func):
    """ Return a wrapped function that raises an deprecation warning when
    called. This should be used for deprecation of module level function names. 
    
    Example ::
    
        >>> def func_a(arg):
        ...    print "This is func_a  (used to be named funcA) called with", arg
        ...
        ...
        >>> funcA = deprecated_function_name(func_a)
        >>> funcA(None)
          
    
    .. note:: This decorator does nothing and if \
        :obj:`Orange.utils.environ.orange_no_deprecated_members` environment \
        variable is set to `True`.
        
    """
    if environ.orange_no_deprecated_members:
        return func
    
    @wraps(func)
    def wrapped(*args, **kwargs):
        warnings.warn("Deprecated function name. Use %r instead!" % func.__name__,
                      DeprecationWarning, stacklevel=2)
        return func(*args, **kwargs)
    return wrapped
    
class ConsoleProgressBar(object):
    """ A class to for printing progress bar reports in the console.
    
    Example ::
    
        >>> import sys, time
        >>> progress = ConsoleProgressBar("Example", output=sys.stdout)
        >>> for i in range(100):
        ...    progress.advance()
        ...    # Or progress.set_state(i)
        ...    time.sleep(0.01)
        ...
        ...
        Example ===================================>100%
        
    """
    def __init__(self, title="", charwidth=40, step=1, output=None):
        """ Initialize the progress bar.
        
        :param title: The title for the progress bar.
        :type title: str
        :param charwidth: The maximum progress bar width in characters.
        
            .. todo:: Get the console width from the ``output`` if the
                information can be retrieved. 
                
        :type charwidth: int
        :param step: A default step used if ``advance`` is called without
            any  arguments
        
        :type step: int
        :param output: The output file. If None (default) then ``sys.stderr``
            is used.
            
        :type output: An file like object to print the progress report to.
         
        """
        self.title = title + " "
        self.charwidth = charwidth
        self.step = step
        self.currstring = ""
        self.state = 0
        if output is None:
            output = sys.stderr
        self.output = output

    def clear(self, i=-1):
        """ Clear the current progress line indicator string.
        """
        try:
            if hasattr(self.output, "isatty") and self.output.isatty():
                self.output.write("\b" * (i if i != -1 else len(self.currstring)))
            else:
                self.output.seek(-i if i != -1 else -len(self.currstring), 2)
        except Exception: ## If for some reason we failed 
            self.output.write("\n")

    def getstring(self):
        """ Return the progress indicator string.
        """
        progchar = int(round(float(self.state) * (self.charwidth - 5) / 100.0))
        return self.title + "=" * (progchar) + ">" + " " * (self.charwidth\
            - 5 - progchar) + "%3i" % int(round(self.state)) + "%"

    def printline(self, string):
        """ Print the ``string`` to the output file.
        """
        try:
            self.clear()
            self.output.write(string)
            self.output.flush()
        except Exception:
            pass
        self.currstring = string

    def __call__(self, newstate=None):
        """ Set the ``newstate`` as the current state of the progress bar.
        ``newstate`` must be in the interval [0, 100].
        
        .. note:: ``set_state`` is the prefered way to set a new steate. 
        
        :param newstate: The new state of the progress bar.
        :type newstate: float
         
        """
        if newstate is None:
            self.advance()
        else:
            self.set_state(newstate)
            
    def set_state(self, newstate):
        """ Set the ``newstate`` as the current state of the progress bar.
        ``newstate`` must be in the interval [0, 100]. 
        
        :param newstate: The new state of the progress bar.
        :type newstate: float
        
        """
        if int(newstate) != int(self.state):
            self.state = newstate
            self.printline(self.getstring())
        else:
            self.state = newstate
            
    def advance(self, step=None):
        """ Advance the current state by ``step``. If ``step`` is None use
        the default step as set at class initialization.
          
        """
        if step is None:
            step = self.step
            
        newstate = self.state + step
        self.set_state(newstate)

    def finish(self):
        """ Finish the progress bar (i.e. set the state to 100 and
        print the final newline to the ``output`` file).
        """
        self.__call__(100)
        self.output.write("\n")

def progress_bar_milestones(count, iterations=100):
    return set([int(i*count/float(iterations)) for i in range(iterations)])

progressBarMilestones = deprecated_function_name(progress_bar_milestones)

import random, types, sys
import time

def getobjectname(x, default=""):
    if type(x)==types.StringType:
        return x
      
    for i in ["name", "shortDescription", "description", "func_doc", "func_name"]:
        if getattr(x, i, ""):
            return getattr(x, i)

    if hasattr(x, "__class__"):
        r = repr(x.__class__)
        if r[1:5]=="type":
            return str(x.__class__)[7:-2]
        elif r[1:6]=="class":
            return str(x.__class__)[8:-2]
    return default


def demangle_examples(x):
    if type(x)==types.TupleType:
        return x
    else:
        return x, 0

def frange(*argw):
    """ Like builtin `range` but works with floats
    """
    start, stop, step = 0.0, 1.0, 0.1
    if len(argw)==1:
        start=step=argw[0]
    elif len(argw)==2:
        stop, step = argw
    elif len(argw)==3:
        start, stop, step = argw
    elif len(argw)>3:
        raise AttributeError, "1-3 arguments expected"

    stop+=1e-10
    i=0
    res=[]
    while 1:
        f=start+i*step
        if f>stop:
            break
        res.append(f)
        i+=1
    return res

verbose = 0

def print_verbose(text, *verb):
    if len(verb) and verb[0] or verbose:
        print text

def lru_cache(maxsize=100):
    """ A least recently used cache function decorator.
    (Similar to the functools.lru_cache in python 3.2)
    """
    
    def decorating_function(func):
        import functools
        cache = {}
        
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = args + tuple(sorted(kwargs.items()))
            if key not in cache:
                res = func(*args, **kwargs)
                cache[key] = (time.time(), res)
                if len(cache) > maxsize:
                    key, (_, _) = min(cache.iteritems(), key=lambda item: item[1][0])
                    del cache[key]
            else:
                _, res = cache[key]
                cache[key] = (time.time(), res) # update the time
                
            return res
        
        def clear():
            cache.clear()
        
        wrapped.clear = clear
        wrapped._cache = cache
        
        return wrapped
    return decorating_function

#from Orange.misc.render import contextmanager
from contextlib import contextmanager

@contextmanager
def member_set(obj, name, val):
    """ A context manager that sets member ``name`` on ``obj`` to ``val``
    and restores the previous value on exit. 
    """
    old_val = getattr(obj, name, val)
    setattr(obj, name, val)
    yield
    setattr(obj, name, old_val)
    
    
class recursion_limit(object):
    """ A context manager that sets a new recursion limit. 
    
    """
    def __init__(self, limit=1000):
        self.limit = limit
        
    def __enter__(self):
        self.old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(self.limit)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.setrecursionlimit(self.old_limit)
        
"""
Some utility functions common to Orange classes.

"""


def _orange_learner__new__(base):
    """Return an 'schizophrenic' __new__ class method following
    `Orange.core.Lerner.__new__` calling convention.

    :param base: base class.
    :type base: type

    """
    import Orange

    @wraps(base.__new__)
    def _orange_learner__new__wrapped(cls, data=None, weight=0, **kwargs):
        self = base.__new__(cls, **kwargs)
        if data is not None:
            self.__init__(**kwargs)
            return self.__call__(data, weight)
        else:
            return self

    return _orange_learner__new__wrapped


def _orange__new__(base=None):
    """Return an orange 'schizophrenic' __new__ class method.

    :param base: base orange class (default `Orange.core.Learner`)
    :type base: type

    Example::
        class NewOrangeLearner(Orange.core.Learner):
            __new__ = _orange__new(Orange.core.Learner)

    """
    import Orange
    if base is None:
        base = Orange.core.Learner

    if issubclass(base, Orange.core.Learner):
        return _orange_learner__new__(base)
    else:
        @wraps(base.__new__)
        def _orange__new_wrapped(cls, data=None, **kwargs):
            if base == object:
                self = base.__new__(cls)
            else:
                self = base.__new__(cls, **kwargs)

            if data:
                self.__init__(**kwargs)
                return self.__call__(data)
            else:
                return self

    return _orange__new_wrapped


def _orange__reduce__(self):
    """ A default __reduce__ method for orange types. Assumes the object
    can be reconstructed with the call `constructor(__dict__)` where __dict__
    if the stored (pickled) __dict__ attribute.

    Example::
        class NewOrangeType(Orange.core.Learner):
            __reduce__ = _orange__reduce()
    """
    return type(self), (), dict(self.__dict__)

demangleExamples = deprecated_function_name(demangle_examples)
printVerbose = deprecated_function_name(print_verbose)

import urllib2
import posixpath
import os

from contextlib import contextmanager
import StringIO

@contextmanager
def finishing(obj):
    """ Calls obj.finish() on context exit.
    """
    yield obj
    obj.finish()

def guess_size(fileobj):
    try:
        if isinstance(fileobj, file):
            return os.fstat(fileobj.fileno()).st_size
        elif isinstance(fileobj, StringIO.StringIO):
            pos = fileobj.tell()
            fileobj.seek(0, 2)
            length = fileobj.tell() - pos
            fileobj.seek(pos, 0)
            return length
        elif isinstance(fileobj, urllib.addinfourl):
            length = fileobj.headers.get("content-length", None)
            return length
    except Exception, ex:
        pass

def copyfileobj(src, dst, buffer=2**10, content_len=None, progress=None):
    """
    shutil.copyfileobj with progress reporting.
    """
    count = 0
    if content_len is None:
        content_len = guess_size(src) or sys.maxint
    while True:
        data = src.read(buffer)
        dst.write(data)
        count += len(data)
        if progress:
            progress(100.0 * count / content_len)
        if not data:
            break
            
def wget(url, directory=".", dst_obj=None, progress=None):
    stream = urllib2.urlopen(url)
    length = stream.headers.get("content-length", None)
    if length is None:
        length = sys.maxint
    else:
        length = int(length)
    
    basename = posixpath.basename(url)
        
    if dst_obj is None:
        dst_obj = open(os.path.join(directory, basename), "wb")
    
    if progress == True:
        from Orange.utils import ConsoleProgressBar
        progress = ConsoleProgressBar("Downloading %r." % basename)
        with finishing(progress):
            copyfileobj(stream, dst_obj, buffer=2**10, content_len=length,
                        progress=progress)
    else:
        copyfileobj(stream, dst_obj, buffer=2**10, content_len=length,
                    progress=progress)
    

import warnings

import selection

import render
