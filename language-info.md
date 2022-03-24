# Shisp Language Information

## Language Grammar notes
### Variable Definitions
Variables are defined by the `let` macro. All Variable names that meet the
following RegEx are valid: `[A-Za-z_-\+\*\/]+[0-9A-Za-z_-\+\*\/]*`

When compiling, any names that are invalid variable names in POSIX Shell
 will be subsituted with the English Name for that character.
For example: '+' -> 'Plus' and '-' -> 'Hyphen'


### Function Definitions
Functions are defined with either the `defun` or `depun` macro. The last
expression in the body of a function is returned.

The exact method of return is implementation defined.

Valid names for methods are the same as variable, with the same rule for
escaping, excepting that it only needs to subsititute invalid function name
characters.

### Macro Definitions

## Standard Library

### Macros
#### Meta
Meta-Macros are an implementation only macro that works on the 'meta' language level.

##### let  
The `let` macro defines a variable within the current scope. 

Usage:
```
(let varname varval)
```

##### defun  
The `defun` macro defines an impure function within the current scope.

An impure function may modify variables globally which may be seen by other functions,
unless called within a pure function.

Usage:
```
(defun name (arglist) body...)
```

##### depun  
The `depun` macro defines a pure function within the current scope.

A pure function may modify variables globally *HOWEVER* any global modifications are
discarded at the end of the function execution. Only functions called within the function
may see modifications made by it or by impure functions called by a pure function. If
another pure function is called, it acts the same as if you called a pure function from
an impure function.

Usage:
```
(depun name (arglist) body...)
```

## Shisp Language Runtime
The Shisp language, as it is designed with features not necessarily available in
shells does contain a 'Language Runtime' known as the Shisp Language Runtime
(SLR). The SLR defines how Shisp code compiles down to Shell in some circumstances.

### Name Mangling  
An implementation *may* provide name mangling for functions and variables to deal
with potential issues without doing so in regular POSIX Shell. If an implementation
choses to do Name Mangling the following conditions MUST be met:

1. The Mangling *MUST* be consistent and dependent upon no outside or random factors.
2. The Mangling *MUST* have some way of determining the original name.
3. The Mangling *MUST* be able to be disabled.

In addition, implementations *MUST* provide the following under the Shebang line in compiled
output if it uses name mangling:
```sh
#shisp::name-mangling={MANGLE_PATTERN}
```
where MANGLE_PATTERN is a pattern able to be used to extract the relevant name in case
conflicting implementations are used.

Implementations may also chose to use 'name comments' in addition to the mangle pattern. 
Name comments take the following form:
`#shisp::name {ORIGINAL} {MANGLED}`
where original is the unmangled name, and mangled is the form as mangled by the compiler.

This may be used in cases where name-mangling is inconsistent with the mangle-pattern,
or where it is required for usage.


### Functions
Shisp has two different types of Functions, impure and pure functions. `defun` will
always make an impure function and `depun` will always make a pure function. 

In Shisp all functions returns the last executed statement/expression.

Impure functions are defined:
```bash
name() {
[arglist]
[body]
[unset arglist]
}
```
where arglist is the arglist for the impure function, body is the function's body
and unset arglist unsets all set arguments.

Pure functions are defined:
```bash
name() (
[arglist]
[body]
[unset arglist]
)
```
where arglist is the arglist for the pure function, body is the function's body
and unset arglist unsets all arguments. Unset arglist *may* be ommitted.

#### Returning Values
When returning values from Functions, the implementation may use one of several methods.


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

## Optimizations
This section describes Optimizations the compiler *can* perform that may otherwise cause issues with
this section and that have additional requirements.

### Impure to Pure functions  

The compiler *can* compile an Impure function as a pure function IF AND ONLY IF:
1. The Function does *NOT* write to any variables that are not defined within that function,
    AND
2. The Function does *NOT* call any other impure functions directly or indirectly 
    OR
3. The Function calls an Impure Function that is able to be compiled to a Pure Function.

A Pure Function can *NOT* be compiled to an Impure Function.

## Shisp Language ABI
