class StackOverflow(Exception):
    pass

class StackUnderflow(Exception):
    pass

class Stack(object):
    def __init__(self, maxsize=1000, items=None, name='No Name'):
        self.items = []
        if items:
            self.items.extend(items)

        self.maxsize = maxsize
        self.name = name

    def size(self):
        return len(self.items)

    def bottom(self):
        if self.items:
            return self.items[0]
        else:
            return None

    def top(self):
        if self.items:
            return self.items[-1]
        else:
            return None

    def flush(self):
        self.items = []

    def dup(self):
        self.push(self.top())

    def pop(self):
        if not self.items:
            raise StackUnderflow('Stack is empty.')
        return self.items.pop()

    def push(self, item):
        if len(self.items) == self.maxsize:
            raise StackOverflow('Stack is full, maxsize: {}'.\
                format(self.maxsize))
        self.items.append(item)

    def isempty(self):
        return len(self.items) == 0

    def __repr__(self):
        return '\033[32mStack {} size: {} maxsize: {}\033[39m\n'.\
            format(self.name, len(self.items), self.maxsize) + \
            '\n'.join(['\033[32m{:4d})\033[39m {}'.format(index, item) \
            for index, item in reversed(list(enumerate(self.items)))]) +\
            '\n\033[32m{}\033[39m'.format('=' * 30)