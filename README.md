![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/pymg-poster.png)

## Table of Contents: <a class="anchor" id="contents"></a>
* [What exactly is pymg?](#what)
* [The Zen of pymg](#zen)
* [How does pymg work?](#work)
* [How to install?](#install)
* [How to use pymg?](#use)


## What exactlry is pymg?<a class="anchor" id="what"></a>
 **pymg** is a **CLI** tool that can interpret Python files and display errors in a
 more **optimized** and more **readable way**.

This tool interprets the selected Python file using the **Python interpreter**
that is already **installed** on the system, and in **case of errors**, it displays
the errors in **separate**, **diverse** and more **readable** forms.

## The zen of pymg<a class="anchor" id="zen"></a>
In the beginning, pymg was created to make the debugging process easier for **blind people**.

If you've ever run a Python file and see the error message that Python produces, you'll notice that it's full of **jumbled** texts. Since the debugging is one of the main tasks of a programmer, surely the debugging process becomes **difficult** with these confusing texts.

**Now imagine how difficult it is for blind people! (Yes there are many blind developers out there)**

The philosophy of pymg is to **simplify**, make **more readable**, **organized** and **separate error messages** that the Python interpreter produces.

Surely people who are sighted can use this tool to debug their projects and even **develop pymg** and provide better and more tools for people who have **more specific needs**.

## How does pymg work?<a class="anchor" id="work"></a>
![img1](https://raw.githubusercontent.com/mimseyedi/pymg/master/docs/how-the-pymg-works.png)

## How to install?<a class="anchor" id="install"></a>
Note that the **Python version** on your system must be `3.11 or higher` to be able to run **pymg**. (In the latest version of Python, more accurate and better error messages are generated)

<a href="https://www.python.org/downloads/">Click here</a> to download the latest version of Python.

You can easily use **pip** to install pymg:
```
python3 -m pip install pymg
```

## How to use pymg?<a class="anchor" id="use"></a>
After you have successfully installed **pymg**, just run it with the **pymg** command like this:
```
pymg my_python_file.py
```
The file is executed with the **Python interpreter** and if an **error occurs**, **pymg** displays the **errors**, otherwise the program **continues** to run.


**pymg** has various **options** for displaying errors, which you can use the `--help` option for more **guidance**:
```
pymg --help
```

