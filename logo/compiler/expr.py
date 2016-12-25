from logo.compiler.stack import Stack
from logo.compiler.lexer import Token, ParseError
from logo.compiler.symbols import Symbol, Operators

class ExprParseError(ParseError):
    pass

class Paren(object):
    def __init__(self, token):
        parens = ['[', ']', '(', ')']
        if not token.value in parens:
            raise ExprParseError('Expected one of {}, found `{}`'.\
                format(parens, token.value), token.line.number, token.colspan)
        self.token = token
        self.value = token.value

    def __repr__(self):
        return '\033[32mParen\033[39m `{}`'.format(self.value)

class Sep(object):
    def __init__(self, token):
        seps = [',']
        if not token.value in seps:
            raise ExprParseError('Expected one of {}, found `{}`'.\
                format(seps, token.value), token.line.number, token.colspan)
        self.token = token
        self.value = token.value

    def __repr__(self):
        return '\033[32mSep\033[39m `{}`'.format(self.value)

class Constant(object):
    def __init__(self, token):
        try:
            value = float(token.value)
        except ValueError, exc:
            raise ExprParseError('Expected integer or variable, found `{}`'.\
                format(token.value),
                token.line.number, token.colspan)
        else:
            self.token = token
            self.value = value

    def evaluate(self, context):
        return self.value

    def __repr__(self):
        return '\033[32mConst\033[39m({})'.format(self.value)

class Variable(object):
    def __init__(self, token):
        if not token.value.startswith(':'):
            raise ExprParseError('Expected Variable to start with colon'+\
                ' `:`, found `{}`'.format(token.value),
                token.line.number, token.colspan)

        if not (token.value) > 1 or not token.value[1].isalpha() \
            or not token.value[1:].isalnum():
            raise ExprParseError('Expected Variable be alphanumeric'+\
                ', found `{}`'.format(token.value),
                token.line.number, token.colspan)

        self.token = token
        self.value = token.value

    def evaluate(self, context):
        return context.evaluate(self.value)

    def __repr__(self):
        return '\033[32mVar\033[39m({})'.format(self.value)

class Operator(object):
    def __init__(self, token):
        symbol = token.value
        operators = Operators()
        symbols = operators.getsymbols() + operators.getfunctions()

        if symbol not in symbols:
            raise ExprParseError('Expected one of {}, found {}'.\
                format(symbols, symbol), token.line.number, token.colspan)

        self.token = token
        self.value = token.value
        self.symbol = operators.getsymbol(self.value)

    def __repr__(self):
        return '\033[32mOp\033[39m({})'.format(self.value)

    def evaluate(self, operands):
        if len(operands) != self.symbol.arity:
            raise RuntimeError('Operator `{}` expected only `{}` operands, found `{}`: {}'.\
                format(self.value, self.symbol.arity, len(operands), operands))
        return self.symbol.evaluate(operands)

class Expression(object):
    def __init__(self, operator, operands):
        self.operator = operator
        self.operands = operands
        self.token = operator.token

    def __repr__(self):
        return '\033[32mExpr\033[39m({}, {})'.format(
            self.operator, self.operands)

    def evaluate(self, context):
        return self.operator.evaluate([operand.evaluate(context)
            for operand in self.operands])

class ExprParser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.stack = Stack(name='`Operator Stack`')
        self.output = Stack(name='`Output Stack`')
        self.reduced = False

    def parse(self):
        # Shunting-yard algorithm
        # While there are tokens to be read:
        operators = Operators()
        self.stack.flush()
        self.output.flush()

        while self.lexer.hastokens():
            # Read a token.
            token = self.lexer.gettoken()

            if not token or token.value in [';', ']']:
                self.lexer.pushtoken(token)
                break

            # If the token is a number, then push it to the output queue.
            if token.value not in operators.getsymbols() + \
                    operators.getfunctions() + ['(', ')', ',']:
                if token.value.startswith(':'):
                    operand = Variable(token)
                else:
                    operand = Constant(token)
                self.output.push(operand)
                self.reduce()

            # If the token is a left parenthesis (i.e. "("), then push it onto the stack.
            elif token.value == '(':
                self.stack.push(Paren(token))

            # If the token is a right parenthesis (i.e. ")"):
            elif token.value == ')':
                # Until the token at the top of the stack is a left parenthesis,
                while not self.stack.isempty():
                    # pop operators off the stack onto the output queue.
                    # If the token at the top of the stack is a function token,
                    # pop it onto the output queue.
                    if self.stack.top().value == '(':
                        self.stack.pop()
                        break

                    operator = self.stack.pop()
                    self.output.push(operator)
                    self.reduce()

                    # Pop the left parenthesis from the stack, but not onto the output queue.
                    if self.stack.isempty():
                        raise ExprParseError('Mismatched parentheses',
                            token.line.number, token.colspan)
                else:
                    # If the stack runs out without finding a left parenthesis,
                    # then there are mismatched parentheses.
                    raise ExprParseError('Mismatched parentheses',
                        token.line.number, token.colspan)

            # If the token is a function argument separator (e.g., a comma):
            elif token.value == ',':
                # Until the token at the top of the stack is a left parenthesis
                while True:
                    if self.stack.top() and self.stack.top().value == '(':
                        break
                    # pop operators off the stack onto the output queue.
                    operator = self.stack.pop()
                    self.output.push(operator)
                    self.reduce()
                else:
                    # If no left parentheses are encountered, either the separator
                    # was misplaced or parentheses were mismatched.
                    raise ExprParseError('Mismatched parentheses or misplaced comma',
                        token.line.number, token.colspan)

            # If the token is a function token, then push it onto the stack.
            elif token.value in Operators().getfunctions():
                operator = Operator(token)
                self.stack.push(operator)

            # If the token is an operator, o1, then:
            elif token.value in Operators().getsymbols():
                operator1 = Operator(token)

                # while there is an operator token o2, at the top of the
                # operator stack and either
                while isinstance(self.stack.top(), Operator):

                    operator2 = self.stack.top()
                    # o1 is left-associative and its precedence is less than or
                    # equal to that of o2, or o1 is right associative, and has
                    # precedence less than that of o2,
                    if (operator1.symbol.associativity == 'LEFT' and
                        operator1.symbol.precedence <= operator2.symbol.precedence)\
                        or (operator1.symbol.associativity == 'RIGHT' and
                            operator1.symbol.precedence < operator2.symbol.precedence):
                        # pop o2 off the operator stack, onto the output queue
                        self.stack.pop()
                        self.output.push(operator2)
                        self.reduce()
                    else:
                        break

                # at the end of iteration push o1 onto the operator stack.
                self.stack.push(operator1)

            # When there are no more tokens to read:
            if self.lexer.hastokens():
                nexttoken = self.lexer.peektoken()
                if token.value not in operators.getsymbols() + \
                    operators.getfunctions() + ['(', ')', ','] and \
                    nexttoken.value not in operators.getsymbols() + \
                    operators.getfunctions() + ['(', ')', ',']:
                    break

                if not nexttoken or nexttoken.value in [';', ']']:
                    break

        # While there are still operator tokens in the stack:
        while not self.stack.isempty():
            # If the operator token on the top of the stack is a parenthesis,
            operator = self.stack.pop()
            if operator.value == '(':
                # then there are mismatched parentheses.
                raise ExprParseError('Mismatched parentheses',
                    operator.token.line.number, operator.token.colspan)
            # Pop the operator onto the output queue.
            self.output.push(operator)
            self.reduce()
        # Exit.

        if self.output.size() > 1:
            # print self.output
            # print self.stack

            raise ParseError('Invalid Expression',
                self.output.top().token.line.number,
                (self.output.bottom().token.colspan[0],
                self.output.top().token.colspan[1]))

        expr = self.output.top()

        self.stack.flush()
        self.output.flush()

        return expr

    def reduce(self):

        if isinstance(self.output.top(), Operator):
            operator = self.output.pop()
            operands = []


            for index in range(operator.symbol.arity):
                if self.output.isempty():
                    raise ParseError('Operator `{}` expected `{}` operands, found only {}'.\
                        format(operator.value, operator.symbol.arity, len(operands)),
                        operator.token.line.number, operator.token.colspan)

                operand = self.output.pop()

                if isinstance(operand, Operator):
                    raise ParseError('Unexpected operator `{}` expected operand for operator `{}`'.\
                        format(operand.value, operator.value),
                        operand.token.line.number, operand.token.colspan)

                operands.append(operand)

            expr = Expression(operator, list(reversed(operands)))
            self.output.push(expr)
            self.reduced = True

if __name__ == '__main__':
    from logo.compiler.lexer import Lexer
    lexer = Lexer()

    expr = ':A + 4'
    lexer.tokenize(expr)

    expr = ExprParser(lexer).parse()
    print expr
    print expr.evaluate(None)

