"""Expression module."""
from functools import singledispatch


class Expression:
    """Expression claas."""

    def __init__(self, *operands):
        self.operands = operands

    def __add__(self, other):
        return Add(self, other if isinstance(other, Expression)
                   else Number(other))

    def __sub__(self, other):
        return Sub(self, other if isinstance(other, Expression)
                   else Number(other))

    def __mul__(self, other):
        return Mul(self, other if isinstance(other, Expression)
                   else Number(other))

    def __truediv__(self, other):
        return Div(self, other if isinstance(other, Expression)
                   else Number(other))

    def __pow__(self, other):
        return Pow(self, other if isinstance(other, Expression)
                   else Number(other))

    def __radd__(self, other):
        return Add(other if isinstance(other, Expression)
                   else Number(other), self)

    def __rsub__(self, other):
        return Sub(other if isinstance(other, Expression)
                   else Number(other), self)

    def __rmul__(self, other):
        return Mul(other if isinstance(other, Expression)
                   else Number(other), self)

    def __rtruediv__(self, other):
        return Div(other if isinstance(other, Expression)
                   else Number(other), self)

    def __rpow__(self, other):
        return Pow(other if isinstance(other, Expression)
                   else Number(other), self)


class Operator(Expression):
    """Subclass Operator."""

    symbol = ""
    precedence = 0

    def __repr__(self):
        return f"{type(self).__name__}{repr(self.operands)}"

    def __str__(self):
        def format_operand(operand):
            if operand.precedence < self.precedence:
                return f"({operand})"
            return str(operand)

        return f" {self.symbol} ".join(format_operand(op)
                                       for op in self.operands)


class Terminal(Expression):
    """Subclass Terminal."""

    precedence = float("inf")

    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)


class Number(Terminal):
    """Subclass Number."""

    def __init__(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Number value must be an int or float.")
        super().__init__(value)


class Symbol(Terminal):
    """Subclass Symbol."""

    def __init__(self, value):
        if not isinstance(value, str):
            raise TypeError("Symbol value must be a string.")
        super().__init__(value)


class Add(Operator):
    """Subclass Add."""

    symbol = "+"
    precedence = 1


class Sub(Operator):
    """Subclass Sub."""

    symbol = "-"
    precedence = 1


class Mul(Operator):
    """Subclass Mul."""

    symbol = "*"
    precedence = 2


class Div(Operator):
    """Subclass Div."""

    symbol = "/"
    precedence = 2


class Pow(Operator):
    """Subclass Pow."""

    symbol = "^"
    precedence = 3


def postvisitor(expr, fn, **kwargs):
    """Postvisitor."""
    stack = [expr]
    visited = {}
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)

        if unvisited_children:
            stack.append(e)
            for children in unvisited_children:
                stack.append(children)
        else:
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)

    return visited[expr]


@singledispatch
def differentiate(expr, *fn, **kwargs):
    """Differentiation."""
    raise NotImplementedError(f"Cannot differentiate {type(expr).__name__}")


@differentiate.register(Number)
def _(expr, *fn, **kwargs):
    return Number(0)


@differentiate.register(Symbol)
def _(expr, *fn, var, **kwargs):
    if expr.value == var:
        return Number(1)
    else:
        return Number(0)


@differentiate.register(Add)
def _(expr, *fn, **kwargs):
    left_diff = differentiate(expr.operands[0], *fn, **kwargs)
    right_diff = differentiate(expr.operands[1], *fn, **kwargs)
    return Add(left_diff, right_diff)


@differentiate.register(Mul)
def _(expr, *fn, **kwargs):
    left_diff = differentiate(expr.operands[0], *fn, **kwargs)
    right_diff = differentiate(expr.operands[1], *fn, **kwargs)
    left = expr.operands[0]
    right = expr.operands[1]
    return Add(Mul(left_diff, right), Mul(left, right_diff))


@differentiate.register(Sub)
def _(expr, *fn, **kwargs):
    left_diff = differentiate(expr.operands[0], *fn, **kwargs)
    right_diff = differentiate(expr.operands[1], *fn, **kwargs)
    return Sub(left_diff, right_diff)


@differentiate.register(Div)
def _(expr, *fn, **kwargs):
    left_diff = differentiate(expr.operands[0], *fn, **kwargs)
    right_diff = differentiate(expr.operands[1], *fn, **kwargs)
    left = expr.operands[0]
    right = expr.operands[1]
    return Div(
        Sub(Mul(right, left_diff), Mul(left, right_diff)),
        Pow(right, Number(2))
    )


@differentiate.register(Pow)
def _(expr, *fn, **kwargs):
    return Mul(expr.operands[1],
               Pow(expr.operands[0],
               Sub(expr.operands[1], Number(1))
                   )
               )
