# 🐙 KrakenScript Syntax Guide

Welcome, brave code divers, to the mysterious depths of KrakenScript! This guide will illuminate the dark waters of our tentacle-twisting language.

## 🌊 Table of Contents

1. [Comments](#-comments)
2. [Variables and Data Types](#-variables-and-data-types)
3. [Functions](#-functions)
4. [Control Structures](#-control-structures)
5. [Error Handling](#-error-handling) (WIP)
6. [Modules and Imports](#-modules-and-imports) (WIP)

## 🐡 Comments

Float your thoughts in bubble comments:

```
(* This is a single-line comment *)

(* This is a
   multi-line
   comment,
   like a jellyfish drifting in the current *)
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

### Type Conversion

Convert between types using built-in functions:

```
let depth_str: String = String(depth);  (* Int to String *)
let temp_int: Int = Int(temperature);   (* Float to Int (truncates) *)
let is_deep: Bool = Bool(depth);        (* Non-zero Int to Bool (true) *)
```

### Variable Scope

Variables are block-scoped within functions and control structures:

```
@ink example() ~
    let x = 10;
    if true ~
        let y = 20;
        print(x);  (* Valid: x is in scope *)
        print(y);  (* Valid: y is in current block *)
    ~
    print(x);  (* Valid: x is still in scope *)
    print(y);  (* Invalid: y is out of scope *)
~
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
    return "Greetings, {creature} of the deep!";
~
```

### Function Calls

Call functions by name with arguments:

```
let pressure: Float = calculate_pressure(5000);
let message: String = greet("Colossal Squid");
```

### Default Parameters

Functions can have default parameter values:

```
@ink explore(depth: Int, time: Int = 60) -> String ~
    return "Explored {depth}m for {time} minutes";
~

let result1 = explore(1000);      (* Uses default time *)
let result2 = explore(1000, 90);  (* Overrides default time *)
```

### Return Values

Functions can return early:

```
@ink check_depth(depth: Int) -> String ~
    if depth < 0 ~
        return "Invalid depth";
    ~
    if depth > 11000 ~
        return "Too deep!";
    ~
    return "Depth is okay";
~
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

Conditions must evaluate to a Boolean value. The `else if` and `else` blocks are optional.

### If-Else Examples

```
let depth: Int = 5000;

if depth > 6000 ~
    print("Welcome to the abyssopelagic zone!");
~ else if depth > 1000 ~
    print("You're in the bathypelagic zone.");
~ else ~
    print("You're still in shallow waters.");
~
```

### Nested If Statements

You can nest if statements for more complex logic:

```
let temperature: Float = 4.5;
let pressure: Float = 500.0;

if depth > 1000 ~
    if temperature < 4.0 ~
        if pressure > 400.0 ~
            print("Cold and high-pressure deep zone detected!");
        ~ else ~
            print("Cold but moderate-pressure zone detected.");
        ~
    ~ else ~
        print("Warm deep zone detected.");
    ~
~ else ~
    print("Shallow waters.");
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
