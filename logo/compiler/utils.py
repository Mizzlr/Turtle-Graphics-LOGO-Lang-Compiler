def indent(lines, skip=0):
    lines = lines.split('\n')
    indented = []
    for index, line in enumerate(lines):
        if index >= skip:
            line = '\t{}'.format(line)
        indented.append(line)
    return '\n'.join(indented)

def listify(alist):
    return '[{}]'.format('\n'.join(map(repr, alist)))