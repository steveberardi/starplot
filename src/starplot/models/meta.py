class Expression:
    def __init__(self, func=None) -> None:
        self.func = func

    def evaluate(self, obj):
        return self.func(obj)

    def __or__(self, other):
        return Expression(func=lambda d: self.evaluate(d) or other.evaluate(d))

    def __and__(self, other):
        return Expression(func=lambda d: self.evaluate(d) and other.evaluate(d))


class Term:
    def _factory(self, func):
        def exp(c):
            value = getattr(c, self.attr)

            if value is None:
                return False

            return func(value)

        return Expression(func=exp)

    def __init__(self, attr):
        self.attr = attr

    def __eq__(self, other):
        return Expression(
            func=lambda c: getattr(c, self.attr) == other
            if other is not None
            else getattr(c, self.attr) is None
        )

    def __ne__(self, other):
        return Expression(
            func=lambda c: getattr(c, self.attr) != other
            if other is not None
            else getattr(c, self.attr) is not None
        )

    def __lt__(self, other):
        return self._factory(lambda value: value < other)

    def __le__(self, other):
        return self._factory(lambda value: value <= other)

    def __gt__(self, other):
        return self._factory(lambda value: value > other)

    def __ge__(self, other):
        return self._factory(lambda value: value >= other)

    def is_in(self, other):
        """Returns `True` if `other` is in the field value"""
        return Expression(func=lambda c: getattr(c, self.attr) in other)

    def is_not_in(self, other):
        """Returns `True` if `other` is NOT in the field value"""
        return Expression(func=lambda c: getattr(c, self.attr) not in other)

    def is_null(self):
        """Returns `True` if the field value is `None`"""
        return Expression(func=lambda c: getattr(c, self.attr) is None)

    def is_not_null(self):
        """Returns `True` if the field value is NOT `None`"""
        return Expression(func=lambda c: getattr(c, self.attr) is not None)


class Meta(type):
    managers = {}

    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)

        if "_manager" in attrs:
            Meta.managers[new_cls] = attrs["_manager"]

        return new_cls

    def __getattribute__(cls, attr):
        if attr == "get":
            return Meta.managers[cls].get

        if attr == "find":
            return Meta.managers[cls].find

        if attr == "all":
            return Meta.managers[cls].all

        return Term(attr)
