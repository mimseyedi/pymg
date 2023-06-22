![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/how-to-use-pymg.png)

## Table of Contents: <a class="anchor" id="contents"></a>
* [Using the --help option](#help)
* [Interpret the file without options](#no_option)
* [Syntax validation using the --syntax option](#syntax)
* [Combination of options](#combine)
  * [Combination of --trace and --inner options with --locals](#T_i_L)
* [Using the --recent option](#recent)
* [Search for a solution with the --search option](#search)
* [Write the output to the file with the --output option](#custom_excepthook)

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
