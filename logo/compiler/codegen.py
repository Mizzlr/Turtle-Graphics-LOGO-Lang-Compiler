from logo.compiler.stack import Stack

class Opcode(object):
    def __init__(self, name, args):
        self.name = name.value
        self.args = args

    def __repr__(self):
        return 'Opcode(\033[32m{}\033[39m, {})'.\
            format(self.name, ','.join(map(
                lambda x: '{:.2f}'.format(x), self.args)))

class Trace(object):
    def __init__(self, context):
        self.line = None
        self.colspan = None
        self.entity = None
        self.error = None
        self.context = context
        self.memento = Stack('`Traceback`')

    def throw(self, error):
        self.error = error
        print self.context.scope
        print self

    def restore(self):
        if not self.memento.isempty():
            prev = self.memento.pop()
            self.line = prev['line']
            self.colspan = prev['colspan']
            self.entity = prev['entity']

    def save(self, line, colspan, entity):
        self.memento.push({
            'line': self.line,
            'colspan': self.colspan,
            'entity': self.entity,
        })

        self.line = line
        self.colspan = colspan
        self.entity = entity

    def __repr__(self):

        representation = ['\033[32mStack Trace:\033[39m']
        index = 0
        for index, trace in enumerate(self.memento.items[1:]):
            line = '{}: In {}, line {}, colspan {}'.\
                format(index, trace['entity'], trace['line'], trace['colspan'])
            representation.append(line)

        index +=1
        line = '{}: In {}, line {}, colspan {}'.\
            format(index, self.entity, self.line, self.colspan)
        representation.append(line)

        representation.append('LogoRuntimeError: {}'.\
            format(repr(self.error)))
        return '\n\n\t'.join(representation)

class Scope(object):
    def __init__(self, context):
        self.context = context
        self.stack = Stack('`Scope Stack`')
        self.variables = {}
        self.stack.push(self.variables)

    def evaluate(self, varname):
        if varname not in self.variables:
            self.context.trace.throw(
                'Variable `{}` not found in current scope.'.format(varname))
        return self.variables[varname]

    def duplicate(self):
        self.stack.push(self.variables.copy())

    def setvar(self, varname, value):
        self.variables[varname] = value

    def restore(self):
        if not self.stack.isempty():
            self.variables = self.stack.pop()

    def __repr__(self):
        return 'Scope({})'.format(self.variables)

class Context(object):
    def __init__(self):
        self.trace = Trace(self)
        self.scope = Scope(self)

    def duplicate(self):
        self.scope.duplicate()

    def savetrace(self, line, colspan, entity):
        self.trace.save(line, colspan, entity)

    def savevar(self, varname, value):
        self.scope.setvar(varname, value)

    def restore(self):
        self.scope.restore()
        self.trace.restore()

    def evaluate(self, varname):
        return self.scope.evaluate(varname)

    def __repr__(self):
        return 'Context({})'.format(self.callstack.top())