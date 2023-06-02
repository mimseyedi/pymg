[![pypi](https://img.shields.io/pypi/v/pymg.svg)](https://pypi.org/project/pymg/) [![license](https://img.shields.io/github/license/mimseyedi/pymg.svg)](https://github.com/mimseyedi/pymg/blob/master/LICENSE)

![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/pymg-poster.png)


## Introduction
 **pymg** is a **CLI** tool that can **interpret** Python files by the **Python interpreter** and display the error message in a **more readable** way if an **exception** occurs.

You can read the following documents to learn more about pymg:

<a href="https://github.com/mimseyedi/pymg/blob/master/docs/guide/how_does_pymg_work.md">How does pymg work</a>

<a href="https://github.com/mimseyedi/pymg/blob/master/docs/guide/how_to_use_pymg.md">How to use pymg</a>

pymg is a free and open source project. Any contribution is welcome. You can do this by registering a pull request.


## Installation
You can use **pip** to install:
```
python3 -m pip install pymg
```


## Example:
Let's check the test.py file as an example:

```python
import sys

def div(a, b):
    return a / b

print(div(int(sys.argv[1]), int(sys.argv[2])))
```

The task of this program is very simple. It passes the two values it receives from the command line arguments to the div function, and the div function divides them.

Now let interpret the test.py file with pymg so that the ZeroDivisionError exception occurs:
```
$ pymg test.py 4 0
```

Output:
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/images/exc-no-option.png)