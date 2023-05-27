![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/pymg-works.png)

## Table of Contents: <a class="anchor" id="contents"></a>
* [How does pymg check syntax?](#syntax)
* [Prioritizing options](#pri_options)
* [Recipe file](#recipe)
* [Source information file](#source_info)
* [Mirror file](#mirror)
* [Interpret the mirror file](#interpret_mirror)
* [Customized excepthook](#custom_excepthook)


## How does pymg check syntax? <a class="anchor" id="syntax"></a>
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

## Customized excepthook <a class="anchor" id="custom_excepthook"></a>
The task of this function is to read the **recipe** and **link** the **commands** to the **functions** whose job is to produce a specific **template**. This function **sends** the **data** related to the **exception** that occurred to the functions that must **generate** the **templates** so that they can easily access this data and **create** the **templates**.
At the end, the **templates** will be **combined** and the output will be displayed.
