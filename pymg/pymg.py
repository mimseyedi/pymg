"""
██████╗ ██╗   ██╗ ███╗   ███╗  ██████╗
██╔══██╗╚██╗ ██╔╝ ████╗ ████║ ██╔════╝
██████╔╝ ╚████╔╝  ██╔████╔██║ ██║  ███╗
██╔═══╝   ╚██╔╝   ██║╚██╔╝██║ ██║   ██║
██║        ██║    ██║ ╚═╝ ██║ ╚██████╔╝
╚═╝        ╚═╝    ╚═╝     ╚═╝  ╚═════╝


pymg is a CLI tool that can interpret Python files and display errors in a more readable form.

This tool interprets the selected Python file using the Python interpreter that is already
installed on the system, and in case of errors, it displays the errors in separate, diverse
and more readable forms.

In short, by replacing the exceptionhook from the sys module with a customized function that
is called when an exception occurs, pymg can access information about exceptions and then display
them in various and separated templates.

For more information about how pymg works:
https://github.com/mimseyedi/pymg/blob/master/docs/guide/how_does_pymg_work.md

For more information about how to use pymg:
https://github.com/mimseyedi/pymg/blob/master/docs/guide/how_to_use_pymg.md

pymg Github repository:
https://github.com/mimseyedi/pymg
"""



import os
import re
import sys
import click
import pickle
import requests
import traceback
import subprocess
from pathlib import Path
from types import TracebackType, ModuleType
try:
    from rich.panel import Panel
    from rich.console import Group
    from rich.syntax import Syntax
    from rich import print as cprint
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], stdout=subprocess.DEVNULL)
finally:
    from rich.panel import Panel
    from rich.console import Group
    from rich.syntax import Syntax
    from rich import print as cprint


MIRROR_FILE: Path = Path(Path(__file__).parent, 'mirror.py')
RECIPE_FILE: Path = Path(Path(__file__).parent, 'recipe.pymgrcp')
SOURCE_INFO: Path = Path(Path(__file__).parent, 'sourceinfo.pymgsinfo')


def read_source(source_file: Path) -> list[str]:
    """
    The task of this function is to read the contents of the Python file
    that the user has chosen for interpretation. This function returns the content
    in the form of a list, whose elements are the codes of each line.

    :param source_file: The path of the python file to be read.
    :return: list[str]
    """

    with open(file=source_file, mode='r') as source_file_:
        source: list = source_file_.readlines()

    return source


def mk_mirror_file(mirror_file: Path, source: list[str], header: list[str]) -> None:
    """
    The task of this function is to create a mirror file with the help of source and header.

    -What is a mirror file?
    A mirror file is a file that contains a specific header and the content of the source file.
    In short, the mirror file is a file that imitates the source file and is interpreted instead
    so that pymg can receive possible exceptions.

    :param mirror_file: The path of the mirror file that is supposed to be interpreted instead of the original file.
    :param source: The path of the python file to be read.
    :param header: The header that is supposed to stick to the beginning of the mirror file.
    :return: None
    """

    mirror_text: list = [*header, *source]

    with open(file=mirror_file, mode='w+') as mirror_file_:
        mirror_file_.write(''.join(mirror_text))


def write_recipe(recipe_file: Path, recipe_data: list[str]) -> None:
    """
    The task of this function is to write the recipe in a file.

    -Note: When an exception occurs, the function that is called determines
    the template of the error with the help of these recipe and then displays it.

    :param recipe_file: The path of the recipe file where the recipe information is supposed to be stored.
    :param recipe_data: A list containing recipe information in string format.
    :return: None
    """

    with open(file=recipe_file, mode='wb') as recipe_file_:
        pickle.dump(recipe_data, recipe_file_)


def read_recipe(recipe_file: Path) -> list[str]:
    """
    The task of this function is to read the file containing the recipe and return it.

    -Note: The recipe is in the form of a list whose elements refer to the functions
    that must be called to create the error template.

    :param recipe_file: The path of the recipe file where the recipe information is stored.
    :return: list[str]
    """

    with open(file=recipe_file, mode='rb') as recipe_file_:
        recipe: list = pickle.load(recipe_file_)

    return recipe


def get_source_info(source_info_file: Path) -> list:
    """
    The task of this function is to read information about the source file.

    -Note: In order to preserve the information of the main file (source) while the mirror file is being
    interpreted, when an exception occurs, this information replaces the information of the mirror file.

    :param source_info_file: The path of the file that contains the information of the main file (source).
    :return: list
    """

    if source_info_file.exists():
        with open(file=source_info_file, mode='rb') as source_info_file_:
            source_information: list = pickle.load(source_info_file_)

        return source_information

    return []


def write_source_info(source_info_file: Path, source_info: tuple) -> None:
    """
    The task of this function is to write the information of the main file (source) in a file.

    -Note: This is done so that the information of the original file (source) is replaced by the
    information of the mirror file during the creation of the template to display the error.

    :param source_info_file: The path of the file that is supposed to keep the information of the main file (source).
    :param source_info: Main file information (source) such as: file name and arguments.
    :return: None
    """

    with open(file=source_info_file, mode='wb') as source_info_file_:
        pickle.dump(source_info, source_info_file_)


def pyfile_path_validator(py_file: Path) -> tuple[bool, str]:
    """
    The task of this function is to validate a Python file.
    This function is to check the Python file that the user presents to pymg for interpretation.

    :param py_file: The path of a python file.
    :return: tuple[bool, str]
    """

    if py_file.exists():
        if py_file.is_file() and py_file.__str__().endswith('.py'):
            return True, 'VALID'

        return False, f'[bold red]Error:[/] The selected path must be the path of a Python file -> [yellow]{py_file.__str__()}[/]'

    return False, f'[bold red]Error:[/] This file does not exist -> [yellow]{py_file.__str__()}[/]'


def check_syntax(source_file: Path, python_interpreter: str) -> tuple[bool, str]:
    """
    The task of this function is to check the syntax of a Python file and return the check result.

    :param source_file: The path of the python file that the user introduced to pymg.
    :param python_interpreter: A Python interpreter that is supposed to do syntax checking.
    :return: tuple[bool, str]
    """

    syntax_err: str = subprocess.run(
        [python_interpreter, '-m', 'py_compile', source_file.__str__()],
        capture_output=True
    ).stderr.decode()

    return (False, syntax_err) if syntax_err else (True, 'INTACT')


def display_syntax_error(source_file: Path, syntax_err: str) -> None:
    """
    The task of this function is to create and finally display
    the error template that shows the syntax error message.

    :param source_file: The path of the python file that the user introduced to pymg.
    :param syntax_err: The syntax error message generated by the Python interpreter.
    :return: None
    """

    extract_digits = lambda string: int(''.join([char for char in string if char.isdigit()]))

    if syntax_err.startswith("Sorry: TabError:"):
        title: str = "TabError"
        splitted_message: list = syntax_err.split("(")
        lineno: int = extract_digits(splitted_message[-1].split(",")[-1])
        code: str = read_source(source_file=source_file)[lineno - 1].strip()
        pointer, message = "    ^", splitted_message[0][16:].strip()

    elif not syntax_err.startswith("Sorry: IndentationError:"):
        title: str = "SyntaxError"
        splitted_message: list = syntax_err[syntax_err.index(',') + 2:].split('\n')
        lineno, code = extract_digits(splitted_message[0].split()[-1]), splitted_message[1].strip()
        pointer, message = splitted_message[2], splitted_message[3][13:]

    else:
        title: str = "IndentationError"
        lineno: int = extract_digits(syntax_err.split(',')[-1][:-1].split()[-1])
        code: str = read_source(source_file=source_file)[lineno - 1].strip()
        pointer, message = "    ^", syntax_err.split(":")[2].split("(")[0].strip()

    main_group = Group(
        Syntax(code=code, lexer='python', line_numbers=True,
               start_line=lineno, highlight_lines={lineno},
               indent_guides=True, background_color='default', theme='gruvbox-dark'),

        pointer if len(str(lineno)) < 2 else " " * (len(str(lineno)) - 1) + pointer,

        '\n' + f'Message: [default]{message.capitalize()}[/]'
    )

    cprint(Panel(
        main_group,
        title=title,
        style='red',
        padding=(1, 1, 1, 1),
        highlight=False
    ))


def gen_type(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the exception type template.
    Every exception that occurs has a type that helps the programmer to classify the error.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    return [
        f"[yellow]Exception Type ❱[/] [bold default]{exc_info.get('exc_type').__name__}[/]"
    ]


def gen_message(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the exception message template.
    Every exception that occurs has a message that helps the programmer to identify and fix the error.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    return [
        f"[yellow]Exception Message ❱[/] [bold default]{exc_info.get('exc_message').__str__()}[/]"
    ]


def gen_file(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate a file template, which displays
    the path of the file where the exception occurred.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    source_path: str = get_source_info(source_info_file=SOURCE_INFO)[0]

    return [
        f"[yellow]File ❱[/] [bold default]{source_path}[/]"
    ]


def gen_scope(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the scope template, which displays
    the name of the scope in which the exception occurred.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    for index in range(len(extracted_tb) - 1, -1, -1):
        if extracted_tb[index].filename == MIRROR_FILE.__str__():
            scope: str = extracted_tb[index].name
            break

    return [
        f"[yellow]Scope ❱[/] [bold default]{scope}[/]"
    ]


def gen_line(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the line template, which displays
    the line number where the exception occurred.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    for index in range(len(extracted_tb) - 1, -1, -1):
        if extracted_tb[index].filename == MIRROR_FILE.__str__():
            lineno: str = str(extracted_tb[index].lineno - 3)
            break

    return [
        f"[yellow]Line ❱[/] [bold default]{lineno}[/]"
    ]


def gen_pointer(tb: traceback.FrameSummary, with_line_number: bool=False) -> str:
    """
    The task of this function is to generate a pointer to the broken part of the code.

    :param tb: A frame from Traceback.
    :param with_line_number: Generating pointer according to line number or not.
    :return: str
    """

    def count_space(string: str) -> int:
        return re.search('\S', string).start()

    lineno, start, end = tb.lineno - 4, tb.colno, tb.end_colno

    inner = True
    if with_line_number:
        if tb.filename == MIRROR_FILE.__str__():
            space: str = " " * (start - count_space(
                string=read_source(source_file=get_source_info(SOURCE_INFO)[0])[lineno]) + 4)
        else:
            space: str = " " * 4
            inner = False

        if len(str(lineno)) >= 2:
            space_for_rich_syntax: str = " " * (len(str(lineno)) - 1)
            space = space_for_rich_syntax + space
    else:
        if tb.filename == MIRROR_FILE.__str__():
            space: str = " " * (start - count_space(
                string=read_source(source_file=get_source_info(SOURCE_INFO)[0])[lineno]))
        else:
            space, inner = "", False

    if inner:
        pointer: str = f"{space}[red]{'^' * (end - start)}[/]"
    else:
        pointer: str = f"{space}[red]{'^' * len(tb.line)}[/]"

    return pointer


def gen_code(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate a code template, which displays
    the code that generated the exception.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    for index in range(len(extracted_tb) - 1, -1, -1):
        if extracted_tb[index].filename == MIRROR_FILE.__str__():
            code: str = extracted_tb[index].line
            tb: traceback.FrameSummary = extracted_tb[index]
            break

    return [
        Syntax(
            code=code, lexer='python', background_color='default', theme='gruvbox-dark'
        ),
        gen_pointer(tb=tb)
    ]


def gen_trace(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate a follow-up template.
    In this format, the occurrence of the exception is tracked, and the information related
    to each part that was influential in the occurrence of the exception will be displayed separately.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    template, counter = [], 0

    template.extend(
        [
            f"[bold yellow]Exception Type ❱[/] [bold default]{exc_info['exc_type'].__name__}[/]",
            f"[bold yellow]Exception Message ❱[/] [bold default]{exc_info['exc_message'].__str__()}[/]"
        ]
    )

    while exc_info['traceback_']:
        trace = Group(
            Panel(
                Group(
                    f"File: [bold default]{get_source_info(source_info_file=SOURCE_INFO)[0]}[/]"
                    if exc_info['traceback_'].tb_frame.f_code.co_filename == MIRROR_FILE.__str__()
                    else f"File: [bold default]{exc_info['traceback_'].tb_frame.f_code.co_filename}[/]",
                    '',

                    Syntax(
                        code=extracted_tb[counter].line, lexer='python',
                        line_numbers=True, start_line=extracted_tb[counter].lineno - 3
                        if extracted_tb[counter].filename == MIRROR_FILE.__str__()
                        else extracted_tb[counter].lineno,

                        highlight_lines={extracted_tb[counter].lineno - 3}
                        if extracted_tb[counter].filename == MIRROR_FILE.__str__()
                        else {extracted_tb[counter].lineno},

                        background_color='default', theme='gruvbox-dark'
                    ),
                    gen_pointer(tb=extracted_tb[counter], with_line_number=True)
                )
            , title=f'[bold]Trace[{counter + 1}] - {extracted_tb[counter].name}[/]', title_align='left',
            padding=(1, 1, 0, 1), style='color(172)')
        )

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

        template.extend(['', trace])

    return template


def gen_trace_with_locals(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the trace template with local variables.
    In this format, the occurrence of the exception is tracked and the information related to each part that affected
    the occurrence of the exception will be displayed separately along with the local variables of each scope.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    template, locals_, counter = [], {}, 0

    template.extend(
        [
            f"[bold yellow]Exception Type ❱[/] [bold default]{exc_info['exc_type'].__name__}[/]",
            f"[bold yellow]Exception Message ❱[/] [bold default]{exc_info['exc_message'].__str__()}[/]"
        ]
    )

    while exc_info['traceback_']:
        locals_[exc_info['traceback_'].tb_frame.f_code.co_name] = {
            var: value for var, value in exc_info['traceback_'].tb_frame.f_locals.items()
            if not var.startswith('__') and not var.endswith('__') and \
               var not in ['display_error_message'] and not isinstance(value, ModuleType)
        }

        trace = Group(
            Panel(
                Group(
                    f"File: [bold default]{get_source_info(source_info_file=SOURCE_INFO)[0]}[/]"
                    if exc_info['traceback_'].tb_frame.f_code.co_filename == MIRROR_FILE.__str__()
                    else f"File: [bold default]{exc_info['traceback_'].tb_frame.f_code.co_filename}[/]",
                    '',

                    Syntax(
                        code=extracted_tb[counter].line, lexer='python',
                        line_numbers=True, start_line=extracted_tb[counter].lineno - 3
                        if extracted_tb[counter].filename == MIRROR_FILE.__str__()
                        else extracted_tb[counter].lineno,

                        highlight_lines={extracted_tb[counter].lineno - 3}
                        if extracted_tb[counter].filename == MIRROR_FILE.__str__()
                        else {extracted_tb[counter].lineno},

                        background_color='default', theme='gruvbox-dark'
                    ),
                    gen_pointer(tb=extracted_tb[counter], with_line_number=True),
                    '',

                    Panel(
                        '\n'.join([f"[bold color(125)]{var}[/] = [italic default]{value}[/]"
                        for var, value in locals_[extracted_tb[counter].name].items()]),
                        expand=False, title='locals', style='yellow'
                    )
                    if extracted_tb[counter].filename == MIRROR_FILE.__str__()
                    else '[bold underline yellow]NO LOCALS WERE FOUND IN THIS TRACE[/]'
                )

            , title=f'[bold]Trace[{counter + 1}] - {extracted_tb[counter].name}[/]', title_align='left',
            padding=(1,1,0,1), style='color(172)')
        )

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

        template.extend(['', trace])

    return template


def gen_inner(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the inner trace template.
    In this format, the exception occurred, limited to the internal space of the main file (source), is tracked, and the
    information related to each part that had an effect on the occurrence of the exception will be displayed separately.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    template, counter = [], 0

    template.extend(
        [
            f"[bold yellow]Exception Type ❱[/] [bold default]{exc_info['exc_type'].__name__}[/]",
            f"[bold yellow]Exception Message ❱[/] [bold default]{exc_info['exc_message'].__str__()}[/]"
        ]
    )

    while exc_info['traceback_']:
        if extracted_tb[counter].filename == MIRROR_FILE.__str__():
            trace = Group(
                Panel(
                    Group(
                        f"File: [bold default]{get_source_info(source_info_file=SOURCE_INFO)[0]}[/]\n",

                        Syntax(
                            code=extracted_tb[counter].line, lexer='python',
                            line_numbers=True, start_line=extracted_tb[counter].lineno - 3,
                            highlight_lines={extracted_tb[counter].lineno - 3},
                            background_color='default', theme='gruvbox-dark'
                        ),
                        gen_pointer(tb=extracted_tb[counter], with_line_number=True)
                    )

                , title=f'[bold]Trace[{counter + 1}] - {extracted_tb[counter].name}[/]', title_align='left',
                padding=(1, 1, 0, 1), style='color(172)')
            )

            template.extend(['', trace])

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

    return template


def gen_inner_with_locals(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the inner trace template with local variables.
    In this format, the exception occurred, limited to the internal space of the main file (source), is tracked, and the
    information related to each part that had an effect on the occurrence of the exception will be displayed separately
    along with the local variables of each scope.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    template, locals_, counter = [], {}, 0

    template.extend(
        [
            f"[bold yellow]Exception Type ❱[/] [bold default]{exc_info['exc_type'].__name__}[/]",
            f"[bold yellow]Exception Message ❱[/] [bold default]{exc_info['exc_message'].__str__()}[/]"
        ]
    )

    while exc_info['traceback_']:
        locals_[exc_info['traceback_'].tb_frame.f_code.co_name] = {
            var: value for var, value in exc_info['traceback_'].tb_frame.f_locals.items()
            if not var.startswith('__') and not var.endswith('__') and \
                var not in ['display_error_message'] and not isinstance(value, ModuleType)
        }

        if extracted_tb[counter].filename == MIRROR_FILE.__str__():
            trace = Group(
                Panel(
                    Group(
                        f"File: [bold default]{get_source_info(source_info_file=SOURCE_INFO)[0]}[/]\n",

                        Syntax(
                            code=extracted_tb[counter].line, lexer='python',
                            line_numbers=True, start_line=extracted_tb[counter].lineno - 3,
                            highlight_lines={extracted_tb[counter].lineno - 3},
                            background_color='default', theme='gruvbox-dark'
                        ),
                        gen_pointer(tb=extracted_tb[counter], with_line_number=True),
                        '',

                        Panel(
                            '\n'.join([f"[bold color(125)]{var}[/] = [italic default]{value}[/]"
                            for var, value in locals_[extracted_tb[counter].name].items()]),
                            expand=False, title='locals', style='yellow'
                        )
                    )

                , title=f'[bold]Trace[{counter + 1}] - {extracted_tb[counter].name}[/]', title_align='left',
                padding=(1, 1, 0, 1), style='color(172)')
            )

            template.extend(['', trace])

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

    return template


def gen_locals(**exc_info: type|Exception|TracebackType) -> list:
    """
    The task of this function is to generate the template of local variables.
    Any exception that occurs can also refer to the last value of variables. This template
    display the last value of each scope variable before the exception occurred.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: list
    """

    extracted_tb: list[traceback.FrameSummary] = traceback.extract_tb(exc_info.get('traceback_'))

    template, locals_, counter = [], {}, 0

    while exc_info['traceback_']:
        locals_[exc_info['traceback_'].tb_frame.f_code.co_name] = {
            var: value for var, value in exc_info['traceback_'].tb_frame.f_locals.items()
            if not var.startswith('__') and not var.endswith('__') and \
               var not in ['display_error_message'] and not isinstance(value, ModuleType)
        }

        if extracted_tb[counter].filename == MIRROR_FILE.__str__():
            local = Group(
                Panel(
                    Group(
                        '\n'.join([f"[bold color(125)]{var}[/] = [italic default]{value}[/]"
                        for var, value in locals_[extracted_tb[counter].name].items()]),
                    )

                , title=f'[bold]{extracted_tb[counter].name} locals[/]', title_align='left',
                padding=(1, 1, 0, 1), style='color(172)')
            )

            template.extend(['', local])

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

    return template


def gen_search(**exc_info: type|Exception|TracebackType) -> None:
    """
    The task of this function is to find and search for a solution in stackoverflow for the exception that occurred with the
    help of this site's APIs. Finally, the title and link of the related posts that received the answer will be displayed.

    :param exc_info: The information related to the exception and error generated by the Python interpreter,
                     which divides this information into three keys: exc_type, exc_message, and traceback_,
                     each of which respectively contains: exception type, exception message, and traceback information.
    :return: None
    """

    try:
        response = requests.get(
            'https://api.stackexchange.com/' +
            f'/2.3/search?order=desc&sort=activity&tagged=python&intitle={exc_info["exc_message"]}&site=stackoverflow')

    except requests.RequestException:
        cprint("[bold red]Error:[/] [default]No internet connection![/]")

    else:
        posts: dict = {
            item.get('title'): item.get('link')
            for item in response.json().get('items')
            if item.get('is_answered')
        }

        search_box = Panel(
            Group(
                '\n'.join(
                    [
                        f'[bold]{title}[/]\n[underline color(33)]{link}[/]\n'
                        for title, link in posts.items()
                    ]
                )
            ),
            title='[bold]Search Result[/]',
            title_align='center',
            padding=(1, 1, 0, 1),
            style='color(29)',
        )

        cprint(search_box)


def get_output(python_interpreter: str, mirror_file: Path, args: list, output_file: Path) -> None:
    """
    The task of this function is to write the output generated by pymg in a text file.

    :param python_interpreter: The Python interpreter that is supposed to interpret the mirror file.
    :param mirror_file: The path of the mirror file to be interpreted.
    :param args: Command line arguments.
    :param output_file: The path of the text file where the output is to be written.
    :return: None
    """

    if output_file.__str__().endswith('.txt') and not output_file.is_dir():
        if not output_file.exists():

            with open(output_file, "w+") as output_file_:
                subprocess.call(
                    [
                        python_interpreter, mirror_file.__str__(), *args

                    ], stdout=output_file_
                )
        else:
            cprint("[bold red]Error:[/] Writing output to text file was not successful!")
            cprint("A file with this name already exists in this path!")
    else:
        cprint("[bold red]Error:[/] Writing output to text file was not successful!")
        cprint("The selected path must be the path of a file with a .txt suffix.")


def interpret(python_interpreter: str, mirror_file: Path, args: list) -> None:
    """
    The task of this function is to interpret (execute) the mirror file.

    :param python_interpreter: The Python interpreter that is supposed to interpret the mirror file.
    :param mirror_file: The path of the mirror file to be interpreted.
    :param args: Command line arguments.
    :return: None
    """

    subprocess.run([python_interpreter, mirror_file.__str__(), *args])


def display_error_message(exc_type: type, exc_message: Exception, traceback_: TracebackType) -> None:
    """
    *** This is a customized exceptionhook function. ***

    The task of this function is to pass the exception information to the functions mentioned in the recipe
    and finally to display the templates that these functions return.

    -Note: When the mirror file is executed, if an exception occurs, the exceptionhook function is called from
    the sys module. But according to the header that the mirror file has, the exceptionhook function is replaced
    with this function (display_error_message) and because of this, 'pymg' can receive information about the exception
    and create messages in its own templates with the help of this replacement.

    :param exc_type: The type of exception that occurred.
    :param exc_message: The message of exception that occurred.
    :param traceback_: A traceback that contains full information about the file where the exception occurred.
    :return: None
    """

    recipe: list = read_recipe(recipe_file=RECIPE_FILE)

    funcs: dict = {
        'type': gen_type, 'message': gen_message,
        'file': gen_file, 'scope': gen_scope,
        'line': gen_line, 'code': gen_code,
        'trace': gen_trace, 'trace_with_locals': gen_trace_with_locals,
        'inner': gen_inner, 'inner_with_locals': gen_inner_with_locals,
        'locals': gen_locals,'search': gen_search
    }

    search_status: bool = False

    if 'search' in recipe:
        search_status = True
        recipe.remove('search')

    if template := [
        list_
        for func in recipe
        for list_ in funcs[func](
            exc_type=exc_type, exc_message=exc_message, traceback_=traceback_
        )
    ]:
        cprint(
            Panel(
                Group(*template),
                title='Exception',
                style='red',
                padding=(0, 1, 0, 1),
                highlight=False
            )
        )

    if search_status:
        gen_search(
            exc_type=exc_type,
            exc_message=exc_message,
            traceback_=traceback_
        )


def prioritizing_options(options: dict) -> list[str]:
    """
    The task of this function is to prioritize between recipes (options).
    This is done for better formatting of messages so that the user can combine
    recipes and produce different outputs.

    :param options: The options from the main function are converted into a dictionary
                    by the click module and are used here after the filter.

    :return: list[str]
    """

    prioritized_options, draft_options, available_options = [], [], [
        option for option, value in options.items() if value
    ]

    for option in available_options:
        if option == 'trace' and 'locals' in available_options:
            if gen_trace in prioritized_options:
                prioritized_options.remove(option)

            prioritized_options.append('trace_with_locals')

        elif option == 'inner' and 'locals' in available_options:
            if gen_inner in prioritized_options:
                prioritized_options.remove(option)

            prioritized_options.append('inner_with_locals')

        elif option == 'trace':
            if gen_trace_with_locals not in prioritized_options:
                prioritized_options.append(option)

        elif option == 'inner':
            if gen_inner_with_locals not in prioritized_options:
                prioritized_options.append(option)

        elif option != 'search':
            draft_options.append(option)

    if not prioritized_options:
        prioritized_options.extend(draft_options)

    if 'search' in available_options:
        prioritized_options.append('search')

    return prioritized_options


def recent_interpretation(python_interpreter: str, mirror_file: Path, args: list,
                          source_info_file: Path, recipe_file: Path) -> None:
    """
    The task of this function is to interpret (execute) the last-recent registered operation.

    :param python_interpreter: The Python interpreter that is supposed to interpret the mirror file.
    :param mirror_file: The path of the mirror file to be interpreted.
    :param args: Command Line arguments.
    :param recipe_file: The path of the recipe file where the recipe information is stored.
    :param source_info_file: The path of the file that contains the information of the main file (source).
    :return: None
    """

    if mirror_file.exists() and recipe_file.exists() and source_info_file.exists():

        source: list = get_source_info(source_info_file=source_info_file)

        if source and Path(source[0]).exists():
            interpret(
                python_interpreter=python_interpreter,
                mirror_file=mirror_file,
                args=args
            )
        else:
            cprint("[bold red]Error:[/] The available information is corrupted.")
    else:
        cprint("[bold red]Error:[/] No information on the last operation is available.")


def gen_mirror_header() -> list[str]:
    """
    The task of this function is to generate a header for the
    mirror file and return it in the form of a list.

    :return: list[str]
    """

    header: list = [
        'import sys\n',
        'from pymg import display_error_message\n',
        'sys.excepthook = display_error_message\n'
    ]

    return header


def get_version() -> str:
    """
    The task of this function is to return the current version of 'pymg'.

    :return: str
    """

    return '1.1.1'


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument('python_file', required=False, nargs=-1)
@click.option('-x', '--syntax', is_flag=True, help="It checks the syntax of the selected Python file. If there is a syntax problem, an error message will be displayed, otherwise 'INTACT' will be displayed.")
@click.option('-t', '--type', is_flag=True, help="The type of exception that occurred will be displayed.")
@click.option('-m', '--message', is_flag=True, help="The message of exception that occurred will be displayed.")
@click.option('-f', '--file', is_flag=True, help="The full path of the Python file where the exception occurred will be displayed.")
@click.option('-s', '--scope', is_flag=True, help="The scope where the exception occurred will be displayed.")
@click.option('-l', '--line', is_flag=True, help="The line number that caused the exception will be displayed.")
@click.option('-c', '--code', is_flag=True, help="The code that caused the exception will be displayed.")
@click.option('-T', '--trace', is_flag=True, help="All paths that contributed to the creation of the exception will be tracked, and then, with separation, each created stack will be displayed.")
@click.option('-i', '--inner', is_flag=True, help="Just like the --trace option, The exception that occurred will be tracked and the result will be limited and displayed to the internal content of the selected Python file.")
@click.option('-L', '--locals', is_flag=True, help="The last value of each scope's local variables before the exception occurs will be displayed. This option can be combined with --trace and --inner.")
@click.option('-S', '--search', is_flag=True, help="With the help of stackoverflow api, the links of answered posts related to the exception that occurred will be displayed.")
@click.option('-o', '--output', nargs=1, type=Path, help="Writes the output to a text file. It has an argument that contains the path of the text file.")
@click.option('-r', '--recent', is_flag=True, help="Redisplays the last operation performed.")
@click.option('-v', '--version', is_flag=True, help='Displays the current version of pymg installed on the system.')
def main(**options):
    """
    pymg is a CLI tool that can interpret Python files by the Python interpreter and display the error message in a more readable way if an exception occurs.
    """

    if options['version'] and not options['python_file']:
        click.echo(get_version())

    elif options['recent'] and not options['python_file']:
        recent_interpretation(
            python_interpreter=sys.executable,
            mirror_file=MIRROR_FILE,
            args=get_source_info(source_info_file=SOURCE_INFO)[1:],
            source_info_file=SOURCE_INFO,
            recipe_file=RECIPE_FILE
        )

    elif options['python_file']:
        if options['version'] or options['recent']:
            click.echo(
                "Usage: pymg [OPTIONS] [PYTHON_FILE]...\nTry 'pymg --help' for help.\n\nError: Two options --version and --recent cannot be used at this stage.")
        else:
            response, file_error_message = pyfile_path_validator(py_file=Path(options['python_file'][0]))

            if response:
                if options['syntax']:
                    response, content = check_syntax(
                        source_file=options['python_file'][0],
                        python_interpreter=sys.executable
                    )

                    cprint(f'[bold green]{content}[/]') if response \
                        else display_syntax_error(
                        source_file=options['python_file'][0],
                        syntax_err=content
                    )

                else:
                    response, syntax_err = check_syntax(
                        source_file=options['python_file'][0],
                        python_interpreter=sys.executable
                    )

                    if response:
                        filtered_options: dict = {
                            option: value
                            for option, value in options.items()
                            if option not in [
                                'python_file', 'syntax', 'output', 'version', 'recent'
                            ]
                        }

                        if recipe := prioritizing_options(
                            options=filtered_options
                        ):
                            write_recipe(recipe_file=RECIPE_FILE, recipe_data=recipe)
                        else:
                            write_recipe(recipe_file=RECIPE_FILE, recipe_data=['inner_with_locals'])

                        source_info: tuple = (
                            Path(os.getcwd(), options['python_file'][0]), *options['python_file'][1:]
                        )

                        write_source_info(source_info_file=SOURCE_INFO, source_info=source_info)

                        mk_mirror_file(
                            mirror_file=MIRROR_FILE,
                            source=read_source(Path(options['python_file'][0])),
                            header=gen_mirror_header()
                        )

                        if options['output'] is not None:
                            output_file: Path = Path(options['output'])
                            get_output(
                                python_interpreter=sys.executable,
                                mirror_file=MIRROR_FILE,
                                args=options['python_file'][1:],
                                output_file=output_file
                            )

                        else:
                            interpret(
                                python_interpreter=sys.executable,
                                mirror_file=MIRROR_FILE,
                                args=options['python_file'][1:]
                            )
                    else:
                        display_syntax_error(
                            source_file=options['python_file'][0],
                            syntax_err=syntax_err
                        )
            else:
                cprint(file_error_message)

    else:
        click.echo("Usage: pymg [OPTIONS] [PYTHON_FILE]...\nTry 'pymg --help' for help.\n\nError: Missing argument 'PYTHON_FILE...'.")


if __name__ == '__main__':
    main()
