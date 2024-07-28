# 🐙 KrakenScript Syntax Guide

Welcome, brave code divers, to the mysterious depths of KrakenScript! This guide will illuminate the dark waters of our tentacle-twisting language.

## 🌊 Table of Contents

- [🐙 KrakenScript Syntax Guide](#-krakenscript-syntax-guide)
  - [🌊 Table of Contents](#-table-of-contents)
  - [🐡 Comments](#-comments)
  - [🦀 Variables and Data Types](#-variables-and-data-types)
    - [Variable Declaration](#variable-declaration)
    - [Data Types](#data-types)
  - [🦑 Functions](#-functions)
    - [Function Declaration](#function-declaration)
    - [Function Examples](#function-examples)
    - [Default Parameters](#default-parameters)
  - [🐋 Control Structures](#-control-structures)
    - [If-Else Currents](#if-else-currents)
    - [For Loops](#for-loops)
  - [🐠 Operators](#-operators)
  - [🦈 String Interpolation](#-string-interpolation)
  - [🐳 Block Delimitation](#-block-delimitation)
  - [🦈 Error Handling (WIP)](#-error-handling-wip)
  - [🐠 Modules and Imports (WIP)](#-modules-and-imports-wip)

## 🐡 Comments

Float your thoughts in bubble comments:

```
(* This is a single-line comment *)

(* This is a
   multi-line
   comment,
   like a jellyfish drifting in the current *)
```

KrakenScript also supports single-line comments using double forward slashes:

```
// This is a single-line comment
```

Comments can be placed anywhere in your code and are ignored by the KrakenScript interpreter.

## 🦀 Variables and Data Types

### Variable Declaration

Declare variables with `let` and constants with `const`:

```
let depth = 1000;
const MARIANA_TRENCH = 11034;
```

Variables must be declared before use. Constants (`const`) cannot be reassigned after declaration.

### Data Types

KrakenScript supports the following basic data types:

1. Boolean: `true` or `false`
2. Float: Decimal numbers
3. Integer: Whole numbers
4. String: Text enclosed in double quotes

```
let is_dark: Bool = true;
let temperature: Float = 4.5;
let creature_count: Int = 500;
let species: String = "Architeuthis dux";
```

Type annotations are optional but recommended for clarity:

```
let depth = 1000;  (* Type inferred as Int *)
let depth: Float = 1000.0;  (* Explicitly typed as Float *)
```

## 🦑 Functions

### Function Declaration

Summon functions using the `@ink` keyword:

```
@ink function_name(param1: Type1, param2: Type2) -> ReturnType ~
    (* Function body *)
    return value;
~
```

Functions must specify parameter types and return type.

### Function Examples

```
@ink calculate_pressure(depth: Float, gravity: Float = 9.8) -> Float ~
    return depth * gravity * 1000;
~

@ink greet(creature: String) -> String ~
    return "Greetings, {{creature}} of the deep!";
~
```

### Default Parameters

Functions can have default parameter values:

```
@ink explore(depth: Int, time: Int = 60) -> String ~
    return "Explored {{depth}}m for {{time}} minutes";
~

let result1 = explore(1000);      (* Uses default time *)
let result2 = explore(1000, 90);  (* Overrides default time *)
```

## 🐋 Control Structures

### If-Else Currents

Navigate your code with if-else statements:

```
if condition ~
    (* Code block executed if condition is true *)
~ else if another_condition ~
    (* Code block executed if another_condition is true *)
~ else ~
    (* Code block executed if all conditions are false *)
~
```

### For Loops

Explore the depths with for loops:

```
for item in collection ~
    (* Code block executed for each item *)
~
```

## 🐠 Operators

KrakenScript supports the following operators:

- Arithmetic: `+`, `-`, `*`, `/`
- Comparison: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Assignment: `=`
- Logical: `&&` (and), `||` (or), `!` (not)

## 🦈 String Interpolation

Embed expressions within strings using double curly braces:

```
let depth = 1000;
let message = "We are {{depth}} meters below the surface.";
```

## 🐳 Block Delimitation

KrakenScript uses the tilde (`~`) for block delimitation:

```
@ink deep_dive(depth: Int) ~
    if depth > 1000 ~
        print("Entering the midnight zone!");
    ~ else ~
        print("Still in the twilight zone.");
    ~
~
```

Remember to use proper indentation for readability, even though KrakenScript uses `~` for block delimitation.

## 🦈 Error Handling (WIP)

This section is still under development. It will cover topics such as:

- Try-catch blocks
- Custom error types
- Error propagation

## 🐠 Modules and Imports (WIP)

This section is still under development. It will cover topics such as:

- Creating modules
- Importing functions and variables from other modules
- Managing dependencies

Stay tuned for updates on these advanced features of KrakenScript!