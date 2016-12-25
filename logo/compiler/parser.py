from logo.compiler.lexer import Lexer, ParseError
from logo.compiler.stack import Stack
from logo.compiler.symbols import Keywords
from logo.compiler.expr import ExprParser, Variable
from logo.compiler.utils import indent, listify
from logo.compiler.codegen import Opcode, Context

class LogoRutimeError(Exception):
    pass

class Parser(object):
    def __init__(self):
        self.lexer = Lexer()
        self.stack = Stack()

    def parse(self, ast, content):
        self.lexer.tokenize(content)

        while self.lexer.hastokens():
            token = self.lexer.peektoken()

            if token.value == 'REPEAT':
                repeat = Repeat(self.lexer)
                repeat.parse(ast)
                repeat.done = False
                ast.addglobals(repeat)
            elif token.value == 'TO':
                proc = Proc(self.lexer)
                proc.parse(ast)
                ast.addproc(proc)
            else:
                if Keywords().getkw(self.lexer.peektoken()):
                    statement = Statement(self.lexer)
                    statement.parse(ast)
                    statement.done = False
                    ast.addglobals(statement)
                else:
                    invocation = Call(self.lexer)
                    invocation.parse(ast)
                    invocation.done = False
                    ast.addglobals(invocation)
        return ast

class Statement(object):
    def __init__(self, lexer):
        self.keyword = None
        self.arguments = []
        self.lexer = lexer

    def __repr__(self):
        return '\033[32mStmt\033[39m({}, {})'.\
            format(self.keyword.value, self.arguments)

    def gencode(self, context):
        context.savetrace(self.keyword.token.line.number,
            self.keyword.token.colspan,
            'Stmt `{}`'.format(self.keyword.value))

        arguments = []
        for argument in self.arguments:
            argument = argument.evaluate(context)
            arguments.append(argument)

        opcode = Opcode(self.keyword, arguments)
        # print context.trace
        # print context.scope

        yield opcode
        context.restore()

    def parse(self, ast):
        self.ast = ast

        while self.lexer.hastokens():

            token = self.lexer.gettoken()
            if token.value == ';':
                break

            keyword = Keywords().getkw(token)
            if not keyword:
                raise ParseError('Expected keyword, found `{}`'.\
                    format(token.value), token.line.number, token.colspan)

            self.keyword = keyword

            exprparser = ExprParser(self.lexer)
            for index in range(self.keyword.arity):
                argument = exprparser.parse()
                self.arguments.append(argument)

            if self.lexer.hastokens():
                token = self.lexer.peektoken()
                if token.value == ';':
                    self.lexer.gettoken()
                break

class Block(object):
    def __init__(self, lexer):
        self.children = []
        self.lexer = lexer

    def __repr__(self):
        children = '\n\t'.join(map(repr, self.children)) \
            if self.children else []
        return '\033[32mBlock\033[39m([{}])'.format(children)

    def gencode(self, context):
        for child in self.children:
            for opcode in child.gencode(context):
                yield opcode
        context.restore()

    def parse(self, ast):
        self.ast = ast

        token = self.lexer.peektoken()
        if token and token.value != '[':
            raise ParseError('Invalid Block begining, expected `[`, found `{}`'.\
                format(token.value), token.line.number, token.colspan)
        self.lexer.gettoken()

        while self.lexer.hastokens():
            token = self.lexer.peektoken()

            if token.value == 'REPEAT':
                repeat = Repeat(self.lexer)
                repeat.parse(ast)
                self.children.append(repeat)
            else:
                if Keywords().getkw(self.lexer.peektoken()):
                    statement = Statement(self.lexer)
                    statement.parse(ast)
                    self.children.append(statement)
                else:
                    invocation = Call(self.lexer)
                    invocation.parse(ast)
                    self.children.append(invocation)

            if not self.lexer.hastokens():
                raise ParseError('Invalid Block ending, expected `]`, found {}'.\
                    format(token.value), token.line.number, token.colspan)

            token = self.lexer.peektoken()
            if token and token.value == ']':
                self.lexer.gettoken()
                break

class Repeat(object):
    def __init__(self, lexer):
        self.count = None
        self.block = None
        self.lexer = lexer
        self.token = None

    def __repr__(self):
        return '\033[32mRepeat\033[39m {} \n\t{})'.\
            format(self.count, self.block)

    def gencode(self, context):
        context.savetrace(self.token.line.number,
            self.token.colspan, 'Repeat')

        for index in range(int(self.count.evaluate(context))):
            context.savevar(':REPCOUNT', index+1)
            for opcode in self.block.gencode(context):
                yield opcode

        context.restore()

    def parse(self, ast):
        self.ast = ast

        while self.lexer.hastokens():
            token = self.lexer.peektoken()
            if token.value != 'REPEAT':
                raise ParseError('Invalid REPEAT construct.',
                    token.line.number, token.colspan)

            self.token = self.lexer.gettoken()

            count = ExprParser(self.lexer).parse()
            if not count:
                raise ParseError('Expected count expression for REPEAT construct.',
                    token.line.number, token.colspan)

            self.count = count

            block = Block(self.lexer)
            block.parse(ast)

            self.block = block

            if self.lexer.hastokens():
                token = self.lexer.peektoken()
                if token.value == ';':
                    self.lexer.gettoken()
                break

class Call(object):
    def __init__(self, lexer):
        self.procname = None
        self.arguments = []
        self.lexer = lexer

    def __repr__(self):
        return '\033[32mCall\033[39m({}, {})'.\
            format(self.procname, self.arguments)

    def gencode(self, context):
        context.savetrace(self.token.line.number,
            self.token.colspan, 'Call `{}`'.format(self.token.value))

        proc = self.ast.getproc(self.procname)

        arguments = []
        for argument in self.arguments:
            if not argument:
                self.ast.delglobal(self)
                raise LogoRutimeError('Proc `{}` takes {} arguments: {}.'.\
                    format(self.procname, len(self.arguments),
                    [arg.value for arg in proc.arguments]))

            argument = argument.evaluate(context)
            arguments.append(argument)

        for var, value in zip(proc.arguments, arguments):
            context.savevar(var.value, value)

        for opcode in proc.gencode(context):
            yield opcode
        context.restore()

    def parse(self, ast):
        self.ast = ast
        while self.lexer.hastokens():

            token = self.lexer.gettoken()
            if token.value == ';':
                break

            if not ast.hasproc(token.value):
                raise ParseError('Proc `{}` not yet defined. Available ones are {}.'.\
                    format(token.value, ast.getprocs()), token.line.number, token.colspan)

            self.token = token
            self.procname = token.value

            exprparser = ExprParser(self.lexer)
            for index in range(ast.getarity(self.procname)):
                argument = exprparser.parse()
                self.arguments.append(argument)

            if self.lexer.hastokens():
                token = self.lexer.peektoken()
                if token.value == ';':
                    self.lexer.gettoken()
                break

class Proc(object):
    def __init__(self, lexer):
        self.name = None
        self.arguments = []
        self.block = None
        self.lexer = lexer

    def __repr__(self):
        return indent('\033[32mProc\033[39m({} {}\n{})'.\
            format(self.name, self.arguments, self.block), skip=1)

    def gencode(self, context):
        context.savetrace(self.token.line.number,
            self.token.colspan, 'Proc `{}`'.format(self.token.value))

        for opcode in self.block.gencode(context):
            yield opcode

        context.restore()

    def parse(self, ast):
        self.ast = ast

        token = self.lexer.peektoken()
        if token and token.value != 'TO':
            raise ParseError('Invalid Proc begining, expected `TO`, found `{}`'.\
                format(token.value), token.line.number, token.colspan)
        self.lexer.gettoken()

        while self.lexer.hastokens():
            token = self.lexer.peektoken()
            if not (token.value and token.value[0].isalpha() and \
                    token.value.isalnum()):
                raise ParseError('Invalid Proc name `{}`.',
                    token.line.number, token.colspan)
            self.name = self.lexer.gettoken().value
            self.token = token

            while self.lexer.hastokens():
                token = self.lexer.peektoken()
                if token.value == '[':
                    break
                elif token.value.startswith(':'):
                    argument = Variable(self.lexer.gettoken())
                    self.arguments.append(argument)
                else:
                    raise ParseError('Expected Variable in the argument list '+\
                    'for Proc `{}`, found `{}`'.format(self.name.value, token),
                    token.line.number, token.colspan)

            block = Block(self.lexer)
            block.parse(ast)
            self.block = block

            if self.lexer.hastokens():
                token = self.lexer.peektoken()
                if token.value == ';':
                    self.lexer.gettoken()
                break

class Ast(object):
    def __init__(self):
        self.procs = []
        self.globals = []

    def merge(self, other):
        for proc in other.procs:
            self.addproc(proc)
        for glob in other.globals:
            self.addglob(glob)

    def addproc(self, proc):
        if self.hasproc(proc.name):
            self.procs.remove(self.getproc(proc.name))
        self.procs.append(proc)

    def addglob(self, glob):
        if glob not in self.globals:
            self.globals.append(glob)

    def addglobals(self, globs):
        self.globals.append(globs)

    def delglobal(self, glob):
        self.globals.remove(glob)

    def hasproc(self, procname):
        for proc in self.procs:
            if procname == proc.name:
                return True
        return False

    def getprocs(self):
        return [proc.name for proc in self.procs]

    def getproc(self, procname):
        for proc in self.procs:
            if procname == proc.name:
                return proc

    def getarity(self, procname):
        for proc in self.procs:
            if procname == proc.name:
                return len(proc.arguments)

    def gencode(self, context):
        for glob in self.globals:
            if not glob.done:
                for opcode in glob.gencode(context):
                    yield opcode
                glob.done = True

    def __repr__(self):
        return '<Ast>\n{}\n{}\n</Ast>'.format(
            listify(self.procs), listify(self.globals))
