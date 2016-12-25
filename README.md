# Turtle-Graphics-LOGO-Lang-Compiler

Python has this module called [turtle](https://docs.python.org/2/library/turtle.html).
[LOGO](https://www.wikiwand.com/en/Logo_(programming_language)) is a programming language, to draw with turtle graphics.
This repo implements a [compiler](logo/compiler) and [runtime](logo/runtime) for LOGO language using python and its turtle module.

The syntax may not be completely compatible with the original, as I have added certain features while removed certain original features. This is just a fun project for the Turtle Graphics with [REPL](logo/runtime/repl.py) for the UI.

# Syntax
`
# This is a comment, comments should be in fresh line only
# RT is for right turn, 90 is the angle to turn right
RT 90
# FD is for forward, 100 is length to move forward
FD 100

# The REPEAT construct, is for looping
# The number 4, instructs to loop 4 times
REPEAT 4 [
  RT 90
  FD 100
]

# The TO construct, is to define procedures
TO SQUARE [
  REPEAT 4 [
    RT 90
    FD 100
  ]
]

# In the above example, the proceduce defines 
# how to draw a square. But this useless if
# we want to draw a square of some size

# :FOO is a variable, while 100 is a literal
# There are no data types, expect FLOAT or INT

# To draw a square of some size, say :SIDE
TO SQUARE :SIDE [
  REPEAT 4 [
    RT 90
    FD :SIDE
  ]
]

# Inside the REPEAT construct, at each loop iteration
# The is an inbuild variable called :REPCOUNT that
# will be available and automatically updated each iteration.

REPEAT 6 [
  RT :REPCOUNT * 60
]

# The above code is same as 
RT 1 * 60
RT 2 * 60
RT 3 * 60
RT 4 * 60
RT 5 * 60
RT 6 * 60

# For simplicity, there are is no IF-THEN-ELSE construct
# There are neither variable assignments, nor booleans

# But, there are expressions which can be placed
# as arguments in place of literals and variables
# Expressions can contain variables and literals, 
# which will be dynamically evaluated.

# Example for expressions, in argument
FD SQRT(100 * :SIDE + :SIDE)

# note the variable such as :SIDE here should be used
# only inside as Procedure, It is best to enclose expressions
# in brackets and also, enclose brackets to be clear about
# the order of evaluation


`

