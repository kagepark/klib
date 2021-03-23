def constructor(*arg_names):
  def __init__(self, *args):
    for name, val in zip(arg_names, args):
      self.__setattr__(name, val)
  return __init__


class MyClass(object):
  __init__ = constructor("var1", "var2", "var3")


c = MyClass("fish", "cheese", "beans")
print(c.var2)
