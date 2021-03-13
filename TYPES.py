#Kage Park
"""
Based on Python2.7 and Python3.x's types module
Inhance for make sure
"""
import sys

NoneType = type(None)
TypeType = type
ObjectType = object

IntType = int
if sys.version_info[0] < 3:
    LongType = long
else:
    LongType = int
FloatType = float
BooleanType = bool
try:
    ComplexType = complex
except NameError:
    pass

StringType = str

# StringTypes is already outdated.  Instead of writing "type(x) in
# types.StringTypes", you should use "isinstance(x, basestring)".  But
# we keep around for compatibility with Python 2.2.
try:
    UnicodeType = unicode
    StringTypes = (StringType, UnicodeType)
except NameError:
    StringTypes = (StringType,)

TupleType = tuple
ListType = list
DictType = DictionaryType = dict

def _f(): pass
FunctionType = type(_f)
LambdaType = type(lambda: None)         # Same as FunctionType
if sys.version_info[0] < 3:
    CodeType = type(_f.func_code)
else:
    CodeType = type(_f.__code__)

def _g():
    yield 1
GeneratorType = type(_g())

class _C:
    def _m(self): pass
ClassType = type(_C)
UnboundMethodType = type(_C._m)         # Same as MethodType
_x = _C()
InstanceType = type(_x)
MethodType = type(_x._m)

BuiltinFunctionType = type(len)
BuiltinMethodType = type([].append)     # Same as BuiltinFunctionType

ModuleType = type(sys)

try:
    raise TypeError
except TypeError:
    tb = sys.exc_info()[2]
    TracebackType = type(tb)
    FrameType = type(tb.tb_frame)
    del tb

SliceType = slice
EllipsisType = type(Ellipsis)

DictProxyType = type(TypeType.__dict__)
NotImplementedType = type(NotImplemented)

# For Jython, the following two types are identical
if sys.version_info[0] < 3:
    GetSetDescriptorType = type(FunctionType.func_code)
    MemberDescriptorType = type(FunctionType.func_globals)
else:
    GetSetDescriptorType = type(FunctionType.__code__)
    MemberDescriptorType = type(FunctionType.__globals__)

del sys, _f, _g, _C, _x                           # Not for export
