# Shisp Language Information
 This document provides a variety of information for the Shisp Programmling Language.

## Syntax Grammar

SYMBOL := `[A-Za-z-_\+\/\*]+[A-Za-z-_\+\/\*]*`;
NUMBER := `[0-9]`;
STRING := ` '"' [^"] '"'`;
ATOM := `SYMBOL | NUMBER | STRING`;
LIST := `'(' SYMBOL* ')'`;
COMMENT := `';' .* '\n'`;

## Special Forms
### let
`(let varname varvalue)`

### defun
`(defun funcname (arglist) body..)`

### depun
`(depun funcname (arglist) body..)`

### shell-literal
`(shell-literal literals..)`

### quote
`(quote ...)`
### quasi-quote
`(quasiquote ...)`

### unquote
`(unquote ...)`

### demac
`(demac name (arglist) body...)`

## Shisp Macro System
 The Shisp Macro Systems does not aim to be hygenic, however it does seek to establish
a basic system for Macros within Shisp. This section describes how it works within Shisp.

 Macros are treated almost the same as regular functions, however they are executed at compile
time. The arglist is what is passed into the macro. If more arguments are passed than argument,
then the compiler *will* issue a warning and attempt to destructure it as much as possible with
the final argument containing the remaining expression as a list. The Compiler *may* issue an error
and cease compilation with an appropriate diagnostic message if chosen to do so.

## Special Variables  
 As shisp compiles to POSIX Shell, some 'special variables' exist that are accessible within
shisp that are not within any scope, but provide information. The variables, their functionality,
and what they should be treated as within the Shell Output is listed.

| Shisp Symbol | POSIX Shell Equivelant |            Meaning                 |
|--------------|------------------------|------------------------------------|
|     fargs    |          $@            | All arguments passed to a function |

## Function Calling and Returning in POSIX Shell  
 Due to limitations within POSIX Shell, Shisp must implement a specific mechanism to allow
for the returning of information other than just numbers from functions. To support this, Shisp requires
the following for usage with Impure Functions and Pure Functions.


### Pure Functions  
 All pure functions return data through the following mechanism: the result of the last expr will be stored
and then be 'returned' to program through printing the result. The resulting output *SHOULD* use the printf
function and use appropiate escaping to ensure errors do not occur. All printf returns *MUST* end in a newline.
The result may be directly stored using a subshell.

### Impure Functions
  All Impure Functions *MUST* return through a specially defined variable for that function that is defined as:
`__{fname}__RVAL_`, where fname is the name of the function. The variable is set to the result of the last
expression through a mechanism that does *NOT* use subshells. An example result is as follows:
```sh
command | read __{fname}__RVAL_
```

when the result is stored in a variable, the code should compile down to calling the function, and *then* assigning
the result to the return variable.

## Types
The following basic types are provided for in Shisp:
- Lists
- Strings
- Numbers
- Symbols
- Atoms
