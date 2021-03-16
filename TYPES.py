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
BoolType = BooleanType = bool
StringType = str
if sys.version_info[0] < 3:
    ByteType=unicode
else:
    ByteType=bytes

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

SliceType = slice
EllipsisType = type(Ellipsis)

DictProxyType = type(TypeType.__dict__)
NotImplementedType = type(NotImplemented)

if sys.version_info[0] < 3:
    GetSetDescriptorType = type(FunctionType.func_code)
    MemberDescriptorType = type(FunctionType.func_globals)
else:
    GetSetDescriptorType = type(FunctionType.__code__)
    MemberDescriptorType = type(FunctionType.__globals__)

del sys, _f, _g, _C, _x                           # Not for export
