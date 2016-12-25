import turtle as tt
from logo.compiler.parser import Parser, Ast
from logo.compiler.codegen import Context

class Turtle(object):
    'Virtual Machine for the Runtime of LOGO lang.'
    def __init__(self):
        self.tt = tt
        self.parser = Parser()
        self.context = Context()
        self.ast = Ast()
        self.speed = 3

    def eval(self, line):
        self.parser = Parser()
        self.drain()
        self.parser.parse(self.ast, line.upper()) # case insensitive
        for opcode in self.ast.gencode(self.context):
            print 'executing ...', opcode
            self.execute(opcode)

    def load(self, filename):
        source = open(filename, 'r').read()
        self.parser = Parser()
        self.parser.parse(self.ast, source.upper())
        for opcode in self.ast.gencode(self.context):
            print 'executing ...', opcode
            self.execute(opcode)

    def drain(self):
        for opcode in self.ast.gencode(self.context):
            print 'draining ...', opcode

    def execute(self, opcode):
        # real comment: very clever metaprogramming!!
        getattr(self.tt, opcode.name.lower())(*opcode.args)
        if opcode.name == 'SPEED':
            self.speed = opcode.args[0]
        elif opcode.name == 'RESET':
            self.tt.speed(self.speed)

if __name__ == '__main__':

    filename = 'samples/polygon.logo'
    turtle = Turtle()
    turtle.load(filename)

