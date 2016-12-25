import copy
import math
import random

class Symbol(object):
    def __init__(self, value, precedence, arity, associativity):
        self.value = value
        self.precedence = precedence
        self.arity = arity
        self.associativity = associativity

    def isoperator(self):
        return not self.value.isalnum()

    def isfunction(self):
        return self.value.isalnum()

    def evaluate(self, operands):
        if self.value == '+':
            return operands[0] + operands[1]
        elif self.value == '-':
            return operands[0] - operands[1]
        elif self.value == '*':
            return operands[0] * operands[1]
        elif self.value == '/':
            return operands[0] / operands[1]
        elif self.value == '%':
            return operands[0] % operands[1]
        elif self.value == '^':
            return operands[0] ** operands[1]
        elif self.value == 'SQRT':
            return math.sqrt(operands[0])
        elif self.value == 'MAX':
            return max(operands[0], operands[1])
        elif self.value == 'MIN':
            return min(operands[0], operands[1])
        elif self.value == 'RAND':
            return random.randint(operands[0], operands[1])
        else:
            raise NotImplementedError('evaluation for operator ' +\
                '`{}` is not defined'.format(self.value))

class Operators(object):
    def __init__(self):
        self.symbols = [
            Symbol('+', 2, 2, 'LEFT'),
            Symbol('-', 2, 2, 'LEFT'),
            Symbol('*', 3, 2, 'LEFT'),
            Symbol('/', 3, 2, 'LEFT'),
            Symbol('%', 3, 2, 'LEFT'),
            Symbol('^', 4, 2, 'RIGHT'),
            Symbol('SQRT', 5, 1, 'RIGHT'),
            Symbol('MAX', 5, 2, 'RIGHT'),
            Symbol('MIN', 5, 2, 'RIGHT'),
            Symbol('RAND', 5, 2, 'RIGHT'),
        ]

    def getsymbols(self):
        return [symbol.value for symbol in self.symbols
            if not symbol.isfunction()]

    def getfunctions(self):
        return [symbol.value for symbol in self.symbols
            if symbol.isfunction()]

    def getsymbol(self, value):
        for symbol in self.symbols:
            if symbol.value == value:
                return symbol
class Keyword(object):
    def __init__(self, value, arity):
        self.value = value
        self.arity = arity
        self.token = None

    def __repr__(self):
        return '\033[32mKeyword\033[39m({}, {})'.format(self.value, self.arity)


class Keywords(object):
    def __init__(self):
        self.keywords = [
            Keyword('RT', 1),
            Keyword('FD', 1),
            Keyword('BK', 1),
            Keyword('LT', 1),
            Keyword('PU', 0),
            Keyword('PD', 0),
            Keyword('CLEAR', 0),
            Keyword('HOME', 0),
            Keyword('RESET', 0),
            Keyword('SPEED', 1),
        ]

    def getkw(self, token):
        for keyword in self.keywords:
            if keyword.value == token.value:
                keyword = copy.deepcopy(keyword)
                keyword.token = token
                return keyword