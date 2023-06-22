[![pypi](https://img.shields.io/pypi/v/pymg.svg)](https://pypi.org/project/pymg/) [![support-version](https://img.shields.io/pypi/pyversions/pymg)](https://img.shields.io/pypi/pyversions/pymg) [![license](https://img.shields.io/github/license/mimseyedi/pymg.svg)](https://github.com/mimseyedi/pymg/blob/master/LICENSE) [![commit](https://img.shields.io/github/last-commit/mimseyedi/pymg)](https://github.com/mimseyedi/pymg/commits/master)


![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/pymg-poster.png)


## Table of Contents: <a class="anchor" id="contents"></a>
* [Introduction](#intro)
* [Installation](#install)
* [How to use pymg?](#usage)
  * [Using the --help option](#help)
  * [Interpret the file without options](#no_option)
  * [Syntax validation using the --syntax option](#syntax)
  * [Combination of options](#combine)
    * [Combination of --trace and --inner options with --locals](#T_i_L)
  * [Using the --recent option](#recent)
  * [Search for a solution with the --search option](#search)
  * [Write the output to the file with the --output option](#custom_excepthook)
* [How does pymg work?](#work)
  * [How does pymg check syntax?](#syntaxx)
  * [Prioritizing options](#pri_options)
  * [Recipe file](#recipe)
  * [Source information file](#source_info)
  * [Mirror file](#mirror)
  * [Interpret the mirror file](#interpret_mirror)
  * [Customized excepthook](#customexcepthook)
* [Bugs/Requests](#cont)
* [License](#license)


## Introduction <a class="anchor" id="intro"></a>
 **pymg** is a **CLI** tool that can **interpret** Python files by the **Python interpreter** and display the error message in a **more readable** way if an **exception** occurs.


## Installation <a class="anchor" id="install"></a>
You can use **pip** to install:
```
python3 -m pip install pymg
```

##  <a class="anchor" id="usage"></a>
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/how-to-use-pymg.png)

## Using the --help option <a class="anchor" id="help"></a>
With the help of the (-h, --help) option, you can easily see how to use pymg and the explanations of the options.

```
Usage: pymg [OPTIONS] [PYTHON_FILE]...

  pymg is a CLI tool that can interpret Python files by the Python interpreter
  and display the error message in a more readable way if an exception occurs.

Options:
  -x, --syntax       It checks the syntax of the selected Python file. If
                     there is a syntax problem, an error message will be
                     displayed, otherwise 'INTACT' will be displayed.
  -t, --type         The type of exception that occurred will be displayed.
  -m, --message      The message of exception that occurred will be displayed.
  -f, --file         The full path of the Python file where the exception
                     occurred will be displayed.
  -s, --scope        The scope where the exception occurred will be displayed.
  -l, --line         The line number that caused the exception will be
                     displayed.
  -c, --code         The code that caused the exception will be displayed.
  -T, --trace        All paths that contributed to the creation of the
                     exception will be tracked, and then, with separation,
                     each created stack will be displayed.
  -i, --inner        Just like the --trace option, The exception that occurred
                     will be tracked and the result will be limited and
                     displayed to the internal content of the selected Python
                     file.
  -L, --locals       The last value of each scope's local variables before the
                     exception occurs will be displayed. This option can be
                     combined with --trace and --inner.
  -S, --search       With the help of stackoverflow api, the links of answered
                     posts related to the exception that occurred will be
                     displayed.
  -o, --output PATH  Writes the output to a text file. It has an argument that
                     contains the path of the text file.
  -r, --recent       Redisplays the last operation performed.
  -v, --version      Displays the current version of pymg installed on the
                     system.
  -h, --help         Show this message and exit.
```
## Interpret the file without options <a class="anchor" id="no_option"></a>
By default, (-i, --inner) and (-L, --locals) will happen if you don't select any options. Combining these two options will make an effective form of error message.

Let's check the test.py file as an example:
```python
import sys

def div(a, b):
    return a / b

print(div(int(sys.argv[1]), int(sys.argv[2])))
```

The task of this program is very simple. It passes the two values it receives from the command line arguments to the div function, and the div function divides them.

Now let us interpret the test.py file with pymg so that the ZeroDivisionError exception occurs.
```
pymg test.py 4 0
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-no-option.png)

## Syntax validation using the --syntax option <a class="anchor" id="syntax"></a>
Let's create an intentional syntax problem in the test.py file:
```python
import sys

def div(a, b):
    return (a / b

print(div(int(sys.argv[1]), int(sys.argv[2])))
```

Now we will use the (-x, --syntax) option:
```
pymg test.py 4 0 -x
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-syntax.png)


SyntaxError always precedes exceptions, and even if you don't use the (-x, --syntax) option, it will be checked at interpret time. 

Pay attention to the following command, which displays a similar output:
```
pymg test.py 4 0
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-syntax.png)

**IndentationError** and **TabError** will also be checked in the syntax checking stage:
```python
import sys

def div(a, b):
return a / b

print(div(int(sys.argv[1]), int(sys.argv[2])))
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-indentation.png)

## Combination of options <a class="anchor" id="combine"></a>
pymg allows you to combine options to access all the features of the exception separately and get different outputs:
```
pymg test.py 4 0 -f -s -l -c -m
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-comb.png)

But some options are ahead of others, you can see the prioritization of options <a href="https://github.com/mimseyedi/pymg/blob/master/docs/guide/how_does_pymg_work.md#pri_options">here</a>.

For example, using the (-T, --trace) option, other options will not work (Because all the options are included in this option):
```
pymg test.py 4 0 -f -s -l -c -m -T
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-trace.png)

## Combination of --trace and --inner options with --locals <a class="anchor" id="T_i_L"></a>
The (-T, --trace) and (-i, --inner) options can be combined with (-L, --locals) option:
```
pymg test.py -i -L
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-inner-locals.png)

## Using the --recent option <a class="anchor" id="recent"></a>
By using the --recent option, you can re-execute the last operation you have done. pymg saves your last move.

## Search for a solution with the --search option <a class="anchor" id="search"></a>
You can search for solutions to your problems in stackoverflow by using the (-S, --search) option. pymg searches stackoverflow for the exception and shows you the title and link of the posts that got the answer:
```
pymg test.py 4 0 -S
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-search.png)

## Write the output to the file with the --output option <a class="anchor" id="syntax"></a>
You can use the (-o, --output) option to write the generated output in a text file:
```
pymg test.py -T -L -o output.txt
```

**output.txt**
```
╭─────────────────────────────────────────── Exception ───────────────────────────────────────────╮
│ Exception Type ❱ JSONDecodeError                                                                │
│ Exception Message ❱ Expecting value: line 1 column 1 (char 0)                                   │
│                                                                                                 │
│ ╭─ Trace[1] - <module> ───────────────────────────────────────────────────────────────────────╮ │
│ │                                                                                             │ │
│ │ File: /Users/mimseyedi/Desktop/test.py                                                      │ │
│ │                                                                                             │ │
│ │ ❱ 8 print(read_json_file(json_file_path))                                                   │ │
│ │           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                    │ │
│ │                                                                                             │ │
│ │ ╭───────────────────────── locals ──────────────────────────╮                               │ │
│ │ │ read_json_file = <function read_json_file at 0x1012705e0> │                               │ │
│ │ │ json_file_path = json_file.json                           │                               │ │
│ │ ╰───────────────────────────────────────────────────────────╯                               │ │
│ ╰─────────────────────────────────────────────────────────────────────────────────────────────╯ │
│                                                                                                 │
│ ╭─ Trace[2] - read_json_file ─────────────────────────────────────────────────────────────────╮ │
│ │                                                                                             │ │
│ │ File: /Users/mimseyedi/Desktop/test.py                                                      │ │
│ │                                                                                             │ │
│ │ ❱ 5 return json.load(jsonf)                                                                 │ │
│ │            ^^^^^^^^^^^^^^^^                                                                 │ │
│ │                                                                                             │ │
│ │ ╭────────────────────────────────── locals ───────────────────────────────────╮             │ │
│ │ │ json_file = json_file.json                                                  │             │ │
│ │ │ jsonf = <_io.TextIOWrapper name='json_file.json' mode='r' encoding='UTF-8'> │             │ │
│ │ ╰─────────────────────────────────────────────────────────────────────────────╯             │ │
│ ╰─────────────────────────────────────────────────────────────────────────────────────────────╯ │
│                                                                                                 │
│ ╭─ Trace[3] - load ───────────────────────────────────────────────────────────────────────────╮ │
│ │                                                                                             │ │
│ │ File: /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/json/__init__.py    │ │
│ │                                                                                             │ │
│ │ ❱ 293 return loads(fp.read(),                                                               │ │
│ │       ^^^^^^^^^^^^^^^^^^^^^^^                                                               │ │
│ │                                                                                             │ │
│ │ NO LOCALS WERE FOUND IN THIS TRACE                                                          │ │
│ ╰─────────────────────────────────────────────────────────────────────────────────────────────╯ │
│                                                                                                 │
│ ╭─ Trace[4] - loads ──────────────────────────────────────────────────────────────────────────╮ │
│ │                                                                                             │ │
│ │ File: /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/json/__init__.py    │ │
│ │                                                                                             │ │
│ │ ❱ 346 return _default_decoder.decode(s)                                                     │ │
│ │       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                     │ │
│ │                                                                                             │ │
│ │ NO LOCALS WERE FOUND IN THIS TRACE                                                          │ │
│ ╰─────────────────────────────────────────────────────────────────────────────────────────────╯ │
│                                                                                                 │
│ ╭─ Trace[5] - decode ─────────────────────────────────────────────────────────────────────────╮ │
│ │                                                                                             │ │
│ │ File: /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/json/decoder.py     │ │
│ │                                                                                             │ │
│ │ ❱ 337 obj, end = self.raw_decode(s, idx=_w(s, 0).end())                                     │ │
│ │       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                     │ │
│ │                                                                                             │ │
│ │ NO LOCALS WERE FOUND IN THIS TRACE                                                          │ │
│ ╰─────────────────────────────────────────────────────────────────────────────────────────────╯ │
│                                                                                                 │
│ ╭─ Trace[6] - raw_decode ─────────────────────────────────────────────────────────────────────╮ │
│ │                                                                                             │ │
│ │ File: /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/json/decoder.py     │ │
│ │                                                                                             │ │
│ │ ❱ 355 raise JSONDecodeError("Expecting value", s, err.value) from None                      │ │
│ │       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                      │ │
│ │                                                                                             │ │
│ │ NO LOCALS WERE FOUND IN THIS TRACE                                                          │ │
│ ╰─────────────────────────────────────────────────────────────────────────────────────────────╯ │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## How does pymg work? <a class="anchor" id="work"></a>
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/pymg-works.png)

## How does pymg check syntax? <a class="anchor" id="syntaxx"></a>
**pymg** uses the **py_compile** module and the **Python interpreter** to make sure that the **syntax** of the Python file is correct.

This will be done with the help of the **subprocess** module and the **output** will be **captured**:

```python
syntax_err: str = subprocess.run(
        [python_interpreter, '-m', 'py_compile', source_file],
        capture_output=True).stderr.decode()
```

## Prioritizing options <a class="anchor" id="pri_options"></a>
Due to the better display of the output, the options selected by the user are **prioritized**, which you will see in the **table** below.

| OPTION        | PRIORITY | DESCRIPTION |
|---------------|----------|-|
| -x, --syntax  | group 1  |It checks the syntax of the selected Python file. If there is a syntax problem, an error message will be displayed, otherwise 'INTACT' will be displayed.|
| -T, --trace   | group 2  |All paths that contributed to the creation of the exception will be tracked, and then, with separation, each created stack will be displayed.|
| -i, --inner   | group 2  |Just like the --trace option, The exception that occurred will be tracked and the result will be limited and displayed to the internal content of the selected Python file.|
| -t, --type    | group 3  |The type of exception that occurred will be displayed.|
| -m, --message | group 3  |The message of exception that occurred will be displayed.|
| -f, --file    | group 3  |The full path of the Python file where the exception occurred will be displayed.|
| -s, --scope   | group 3  |The scope where the exception occurred will be displayed.|
| -l, --line    | group 3  |The line number that caused the exception will be displayed.|
| -c, --code    | group 3  |The code that caused the exception will be displayed.|
| -L, --locals  | group 3  |The last value of each scope's local variables before the exception occurs will be displayed. This option can be combined with --trace and --inner.|
| -S, --search  | group 4  |With the help of stackoverflow api, the links of answered posts related to the exception that occurred will be displayed.|


## Recipe file <a class="anchor" id="recipe"></a>
After **prioritization** and modification, the options are **stored** as pointers to a **template** (the function that creates the specified template) in a file called **recipe**.

The **recipe** later helps the called function to create the **templates** according to the **recipe** when an **exception** occurs.

## Source information file <a class="anchor" id="source_info"></a>
In order to **access** the **information** of the **main file (source)**, such as the **file name** and command line **arguments**, a file containing the source information is created to **replace** the information related to the **mirror** file.

## Mirror file <a class="anchor" id="mirror"></a>
A **mirror** file is a file that **imitates** the **source**.

In order to **capture** the data of the **exception** that occurred, a piece of code must be **added** to the source:

```python
import sys
from pymg import display_error_message
sys.excepthook = display_error_message
```

The task of this piece of code is to **replace** the **excepthook** function from the **sys** module with a **customized** function.

**Note: When an exception occurs, the excepthook function of the sys module will be executed.**

Since you should not **touch** the **main file (source)** and make **changes** in it, a file named **mirror** file will be **created**, which contains a **header** (the piece of code you saw above) and the **source content**. This file is interpreted **instead** of the **source** file so that the source remains **isolated** and **not damaged**.

## Interpret the mirror file <a class="anchor" id="interpret_mirror"></a>
The **mirror** file will be **interpreted** (executed) by the **Python interpreter**, and if an **exception** occurs, the **display_error_message** function will be called **instead** of **excepthook**. Next, by reading the **recipe**, this function will find out what functions to call to **generate** the **template**, and at the end, it will display the **template** that contains the information **requested** by the user.

## Customized excepthook <a class="anchor" id="customexcepthook"></a>
The task of this function is to read the **recipe** and **link** the **commands** to the **functions** whose job is to produce a specific **template**. This function **sends** the **data** related to the **exception** that occurred to the functions that must **generate** the **templates** so that they can easily access this data and **create** the **templates**.
At the end, the **templates** will be **combined** and the output will be displayed.

## Bugs/Requests <a class="anchor" id="cont"></a>
Please send bug reports and feature requests through <a href="https://github.com/mimseyedi/pymg/issues">github issue tracker</a>.

## License <a class="anchor" id="license"></a>
pymg is a free and open source project under the `GPL-3 LICENSE`. Any contribution is welcome. You can do this by registering a pull request.