# Shisp Language Information

## Language Grammar notes
### Variable Definitions
Variables are defined with:
`defvar`

### Function Definitions
Functions are defined with:
`defun`

you may also use

`depfun` for 'pure' functions.

### Macro Definitions

## Standard Library
To be written

## Shisp Language Runtime
The Shisp language, as it is designed with features not necessarily available in
shells does contain a 'Language Runtime' known as the Shisp Language Runtime
(SLR). The SLR defines how Shisp code compiles down to Shell in some circumstances.

### Returning Values 
When returning values from Functions the runtime provides a variable for each function
called `__{FUNCTION_NAME}_RETVAL` where Function Name is the cannonical version of the
function name *after* any modifications have been made internally. These variables are
considered write once and read once, and may only be read after the function is called.
The variable *may* be omitted IF and ONLY IF the following conditions are met:
- The function *does not* return any actual values deliberately 
    OR
- The function *ONLY* returns numbers, in which case the default POSIX return
   mechanism may be used

### Pure Functions  
Pure functions use the alternative POSIX Function syntax for using a subshell when
compiled, UNLESS they pass back a non-integer return value. In which case it may either
- Use a regular POSIX Shell Function definition, and use custom variables that are created/destroyed
   at the start and end of functions to prevent actual modifications, except for the return variable.
     -OR-
- Use the subshell syntax and use temporary functions or some other mechanism to pass information back
   to a stub-function that handles the return variable.
     -OR-
- Use a stub function that stores a copy of all variables accessible to the function.

### Impure to Pure functions  
The compiler *may* compile an Impure function to a Pure function Provided the following conditions are met:
- The Function does *NOT* write to any variables that are not defined in that function,
- The Function does *NOT* call any impure function

## Shisp Language ABI
