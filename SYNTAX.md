# 🚀 KrakenScript Syntax

## 📚 Table of Contents
- [🚀 KrakenScript Syntax](#-krakenscript-syntax)
  - [📚 Table of Contents](#-table-of-contents)
  - [🏗️ Basic Structure](#️-basic-structure)
  - [🔠 Variables and Constants](#-variables-and-constants)
  - [🧮 Data Types](#-data-types)
  - [🔧 Functions](#-functions)
  - [🔀 Control Structures](#-control-structures)
    - [If Statements](#if-statements)
  - [🏛️ Classes](#️-classes)
  - [📦 Modules](#-modules)
  - [⚠️ Error Handling](#️-error-handling)
  - [🌟 Special Features](#-special-features)

## 🏗️ Basic Structure

> **Note:** This section is a work in progress.

## 🔠 Variables and Constants

Declare variables and constants with ease:

```
var x = 5
const y = "Hello"
```

Variables are mutable, while constants are immutable.

## 🧮 Data Types

KrakenScript supports the following data types:

| Type | Example | Description |
|------|---------|-------------|
| num  | 42, 3.14 | Numbers (integer or float) |
| text | "Hello, Kraken!" | Text strings |
| bool | true, false | Boolean values |
| list | [1, 2, 3] | Ordered collection **WIP**|
| map  | {key: value} | Key-value pairs **WIP** |

## 🔧 Functions

Define functions with the `func` keyword:

```
func hello() 
    print("Hello, world!")

func add(a, b) -> num
    return a + b

func subtract(a: Float, b: Float) -> Float
    return a - b
```

Functions can have optional return type annotations.

## 🔀 Control Structures

### If Statements

KrakenScript uses indentation to define code blocks in if statements:

```
if condition
    # code executed if condition is true
elif another_condition
    # code executed if another_condition is true
else
    # code executed if all conditions are false
```

You can also use if statements without elif or else:

```
if condition
    # code executed if condition is true
```

For single-line conditionals, you can use a compact form:

```
if condition => print("Condition is true")
```

> **Note:** Other control structures are still a work in progress.

## 🏛️ Classes

> **Note:** This section is a work in progress.

## 📦 Modules

> **Note:** This section is a work in progress.

## ⚠️ Error Handling

> **Note:** This section is a work in progress.

## 🌟 Special Features

> **Note:** This section is a work in progress.

---

📝 **Note:** KrakenScript is under active development. Syntax and features may change.