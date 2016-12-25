from logo.compiler.stack import Stack
from logo.compiler.symbols import Operators

class ParseError(Exception):
    def __init__(self, message, number, colspan):
        self.message = message
        self.number = number
        self.colspan = colspan
        super(ParseError, self).__init__(repr(self))

    def __repr__(self):
        if self.colspan[0] == self.colspan[1]:
            colinfo = 'at column {}'.format(self.colspan[0])
        else:
            colinfo = 'from column {} to {}'.format(*self.colspan)
        return '{}, in line {}, {}'.\
            format(self.message, self.number, colinfo)

class Token(object):
    def __init__(self, chars):
        self.value = None
        self.colspan = None
        self.line = None

        if chars:
            self.value = ''.join([char[0] for char in chars])
            self.colspan = (chars[0][1], chars[-1][1])

    def __repr__(self):
        return 'Token({}, {})'.format(self.value, self.colspan)

class Line(object):
    def __init__(self, number, content):
        self.number = number
        self.tokens = self.tokenize(content)
        for token in self.tokens:
            token.line = self

    def tokenize(self, content):
        tokens = []
        content = zip(content, range(1, len(content)+1))
        chars = []
        operators = Operators()
        for char in content:
            if char[0] in operators.getsymbols() + \
                    ['(', ')', ',', '[', ']', ';']:
                chars.append((' ', None))
                chars.append(char)
                chars.append((' ', None))
            else:
                chars.append(char)

        content = chars
        chars = []

        for char in content:

            if char[0] in [' ', '\t']:
                tokens.append(Token(chars))
                chars = []
            else:
                chars.append(char)

        tokens.append(Token(chars))

        tokens = [token for token in tokens if token.value]
        return tokens

    def __repr__(self):
        return 'Line({}, {})'.format(self.number, self.tokens)

class Lexer(object):
    def __init__(self):
        self.lines = []
        self.stack = Stack(name='`Lexer Stack`')

    def tokenize(self, source):
        lines = []
        for number, line in enumerate(source.split('\n')):

            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            line = Line(number + 1, line)
            lines.append(line)

        self.lines = lines

        for line in reversed(self.lines):
            for token in reversed(line.tokens):
                self.stack.push(token)

    def peektoken(self):
        return self.stack.top()

    def gettoken(self):
        return self.stack.pop()

    def pushtoken(self, token):
        self.stack.push(token)

    def hastokens(self):
        return not self.stack.isempty()
