import cmd2
import signal
from logo.runtime.vm import Turtle

class Repl(cmd2.Cmd):
    intro = '\033[36m    /\\       **** Welcome to LOGO repl. ****\n' +\
    '   /  \\         ...  cherishing the memories\n' +\
    '  /_TT_\\        of turtle graphics -- Mizzlr\n\033[32m'

    prompt = '\033[32mlogo[\033[39m1\033[32m]:> \033[39m'
    terminators = []

    def preloop(self):
        self.count = 1
        self.turtle = Turtle()

    def do_load(self, line):

        if not line:
            print 'Usage: load <filename>'
            print 'Example: load sample.logo'
        else:
            self.turtle.load(line)

    def do_ast(self, line):
        print self.turtle.ast

    def do_quit(self, line):
        print '\033[36mBye bye. Happy turtling\033[39m'
        return True

    def do_exit(self, line):
        return self.do_quit(line)

    def default(self, line):
        self.turtle.eval(line)

    def postcmd(self, stop, line):
        self.count += 1
        self.prompt = '\033[32mlogo[\033[39m{}\033[32m]:> \033[39m'.\
            format(self.count)
        if line.startswith('exit') or line.startswith('quit') or stop:
            return True

if __name__ == '__main__':

    repl = Repl()
    repl.cmdloop()
