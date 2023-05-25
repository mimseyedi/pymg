"""
██████╗ ██╗   ██╗ ███╗   ███╗  ██████╗
██╔══██╗╚██╗ ██╔╝ ████╗ ████║ ██╔════╝
██████╔╝ ╚████╔╝  ██╔████╔██║ ██║  ███╗
██╔═══╝   ╚██╔╝   ██║╚██╔╝██║ ██║   ██║
██║        ██║    ██║ ╚═╝ ██║ ╚██████╔╝
╚═╝        ╚═╝    ╚═╝     ╚═╝  ╚═════╝


pymg is a CLI tool that can interpret Python files and display errors in a more readable form.

This tool interprets the selected Python file using the Python interpreter
that is already installed on the system, and in case of errors, it displays
the errors in separate, diverse and more readable forms.

pymg Github repository: https://github.com/mimseyedi/pymg
"""


import sys
import click
import pickle
import requests
import traceback
import subprocess
from pathlib import Path
from typing import Callable
from types import TracebackType, ModuleType
from rich.panel import Panel
from rich.console import Group
from rich.syntax import Syntax
from rich import print as cprint


MIRROR_FILE: Path = Path(Path(__file__).parent, 'mirror.py')
RECIPE_FILE: Path = Path(Path(__file__).parent, 'recipe.pymgrcp')
PYFILE_INFO: Path = Path(Path(__file__).parent, 'pyfileinfo.pymginfo')


def read_source(source_file: Path) -> list[str]:
    with open(file=source_file, mode='r') as source_file_:
        source: list = source_file_.readlines()

    return source


def mk_mirror_file(mirror_file: Path, source: list[str], header: list[str]) -> None:

    mirror_text: list = [*header, *source]

    with open(file=mirror_file, mode='w+') as mirror_file_:
        mirror_file_.write(''.join(mirror_text))


def write_recipe(recipe_file: Path, recipe_data: list[Callable]) -> None:
    with open(file=recipe_file, mode='wb') as recipe_file_:
        pickle.dump(recipe_data, recipe_file_)


def read_recipe(recipe_file: Path) -> list[Callable]:
    with open(file=recipe_file, mode='rb') as recipe_file_:
        recipe: list = pickle.load(recipe_file_)

    return recipe


def get_file_path(py_file_info: Path) -> list:
    with open(file=py_file_info, mode='rb') as py_file_info_:
        py_file_information: list = pickle.load(py_file_info_)

    return py_file_information


def write_file_info(py_file_info: Path, file_path: str) -> None:
    with open(file=py_file_info, mode='wb') as py_file_info_:
        pickle.dump(file_path, py_file_info_)


def pyfile_path_validator(py_file: Path) -> tuple[bool, str]:
    if py_file.exists():
        if py_file.is_file() and py_file.__str__().endswith('.py'):
            return True, 'VALID'

        return False, f'[bold red]Error:[/] The selected path must be the path of a Python file -> [yellow]{py_file.__str__()}[/]'

    return False, f'[bold red]Error:[/] This file does not exist -> [yellow]{py_file.__str__()}[/]'


def check_syntax(source_file: Path, python_interpreter: str) -> tuple[bool, str]:
    syntax_err: str = subprocess.run(
        [python_interpreter, '-m', 'py_compile', source_file.__str__()],
        capture_output=True
    ).stderr.decode()

    return (True, 'INTACT') if not syntax_err else (False, syntax_err)


def display_syntax_error(syntax_err: str) -> None:
    splitted_message: list = syntax_err[syntax_err.index(',') + 2:].split('\n')

    lineno: int = int(splitted_message[0].split()[-1])

    main_group = Group(
        Syntax(splitted_message[1].strip(), lexer='python', line_numbers=True,
               start_line=lineno, highlight_lines={lineno},
               indent_guides=True, background_color='default', theme='gruvbox-dark'),

        splitted_message[2] if len(str(lineno)) < 2 else " " * (len(str(lineno)) - 1) + splitted_message[2],

        '\n' + f'Message: [default]{splitted_message[3][13:].capitalize()}[/]'
    )

    cprint(Panel(main_group, title='SyntaxError', style='red', padding=(1, 1, 1, 1), highlight=False))


def gen_type(**exc_info) -> list:
    return [
        f"[yellow]Exception Type ❱[/] [bold default]{exc_info['exc_type'].__name__}[/]"
    ]


def gen_message(**exc_info) -> list:
    return [
        f"[yellow]Exception Message ❱[/] [bold default]{exc_info['exc_message'].__str__()}[/]"
    ]


def gen_file(**exc_info) -> list:
    py_file_path: str = get_file_path(py_file_info=PYFILE_INFO)

    return [
        f"[yellow]File ❱[/] [bold default]{py_file_path}[/]"
    ]


def gen_scope(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

    for index in range(len(extracted_tb) - 1, -1, -1):
        if extracted_tb[index].filename == MIRROR_FILE.__str__():
            scope: str = extracted_tb[index].name
            break

    return [
        f"[yellow]File ❱[/] [bold default]{scope}[/]"
    ]


def gen_line(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

    for index in range(len(extracted_tb) - 1, -1, -1):
        if extracted_tb[index].filename == MIRROR_FILE.__str__():
            lineno: str = str(extracted_tb[index].lineno - 3)
            break

    return [
        f"[yellow]Line ❱[/] [bold default]{lineno}[/]"
    ]


def gen_code(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

    for index in range(len(extracted_tb) - 1, -1, -1):
        if extracted_tb[index].filename == MIRROR_FILE.__str__():
            code: str = extracted_tb[index].line
            break

    return [
        Syntax(
            code=code, lexer='python', background_color='default', theme='gruvbox-dark'
        )
    ]


def gen_trace(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

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
                    f"File: [bold default]{get_file_path(py_file_info=PYFILE_INFO)}[/]"
                    if exc_info['traceback_'].tb_frame.f_code.co_filename == MIRROR_FILE
                    else f"File: [bold default]{exc_info['traceback_'].tb_frame.f_code.co_filename}[/]",
                    '',

                    Syntax(
                        code=extracted_tb[counter].line, lexer='python',
                        line_numbers=True, start_line=extracted_tb[counter].lineno - 3
                        if extracted_tb[counter].filename == get_file_path(PYFILE_INFO)
                        else extracted_tb[counter].lineno,

                        highlight_lines={extracted_tb[counter].lineno - 3}
                        if extracted_tb[counter].filename == get_file_path(PYFILE_INFO)
                        else {extracted_tb[counter].lineno},

                        background_color='default', theme='gruvbox-dark'
                    )
                )
            , title=f'[bold]Trace[{counter + 1}] - {extracted_tb[counter].name}[/]', title_align='left',
            padding=(1, 1, 0, 1), style='color(172)')
        )

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

        template.extend(['', trace])

    return template


def gen_trace_with_locals(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

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
                    f"File: [bold default]{get_file_path(py_file_info=PYFILE_INFO)}[/]"
                    if exc_info['traceback_'].tb_frame.f_code.co_filename == MIRROR_FILE
                    else f"File: [bold default]{exc_info['traceback_'].tb_frame.f_code.co_filename}[/]",
                    '',

                    Syntax(
                        code=extracted_tb[counter].line, lexer='python',
                        line_numbers=True, start_line=extracted_tb[counter].lineno - 3
                        if extracted_tb[counter].filename == get_file_path(PYFILE_INFO)
                        else extracted_tb[counter].lineno,

                        highlight_lines={extracted_tb[counter].lineno - 3}
                        if extracted_tb[counter].filename == get_file_path(PYFILE_INFO)
                        else {extracted_tb[counter].lineno},

                        background_color='default', theme='gruvbox-dark'
                    ),
                    '',

                    Panel(
                        '\n'.join([f"[bold color(125)]{var}[/] = [italic default]{value}[/]"
                        for var, value in locals_[extracted_tb[counter].name].items()]),
                        expand=False, title='locals', style='yellow'
                    )
                    if extracted_tb[counter].filename == get_file_path(PYFILE_INFO)
                    else '[bold underline yellow]NO LOCALS WERE FOUND IN THIS TRACE[/]'
                )

            , title=f'[bold]Trace[{counter + 1}] - {extracted_tb[counter].name}[/]', title_align='left',
            padding=(1,1,0,1), style='color(172)')
        )

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

        template.extend(['', trace])

    return template


def gen_inner(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

    template, counter = [], 0

    template.extend(
        [
            f"[bold yellow]Exception Type ❱[/] [bold default]{exc_info['exc_type'].__name__}[/]",
            f"[bold yellow]Exception Message ❱[/] [bold default]{exc_info['exc_message'].__str__()}[/]"
        ]
    )

    while exc_info['traceback_']:
        if extracted_tb[counter].filename == get_file_path(PYFILE_INFO):
            trace = Group(
                Panel(
                    Group(
                        f"File: [bold default]{get_file_path(PYFILE_INFO)}[/]\n",

                        Syntax(
                            code=extracted_tb[counter].line, lexer='python',
                            line_numbers=True, start_line=extracted_tb[counter].lineno - 3,
                            highlight_lines={extracted_tb[counter].lineno - 3},
                            background_color='default', theme='gruvbox-dark'
                        )
                    )

                , title=f'[bold]Trace[{counter + 1}] - {extracted_tb[counter].name}[/]', title_align='left',
                padding=(1, 1, 0, 1), style='color(172)')
            )

            template.extend(['', trace])

        counter += 1

        exc_info['traceback_'] = exc_info['traceback_'].tb_next

    return template


def gen_inner_with_locals(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

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

        if extracted_tb[counter].filename == get_file_path(PYFILE_INFO):
            trace = Group(
                Panel(
                    Group(
                        f"File: [bold default]{get_file_path(PYFILE_INFO)}[/]\n",

                        Syntax(
                            code=extracted_tb[counter].line, lexer='python',
                            line_numbers=True, start_line=extracted_tb[counter].lineno - 3,
                            highlight_lines={extracted_tb[counter].lineno - 3},
                            background_color='default', theme='gruvbox-dark'
                        ),
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


def gen_locals(**exc_info) -> list:
    extracted_tb: list = traceback.extract_tb(exc_info['traceback_'])

    template, locals_, counter = [], {}, 0

    while exc_info['traceback_']:
        locals_[exc_info['traceback_'].tb_frame.f_code.co_name] = {
            var: value for var, value in exc_info['traceback_'].tb_frame.f_locals.items()
            if not var.startswith('__') and not var.endswith('__') and \
               var not in ['display_error_message'] and not isinstance(value, ModuleType)
        }

        if extracted_tb[counter].filename == get_file_path(PYFILE_INFO):
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


def gen_search(**exc_info) -> None:
    try:
        response = requests.get(
            'https://api.stackexchange.com/' +
            f'/2.3/search?order=desc&sort=activity&tagged=python&intitle={exc_info["exc_message"]}&site=stackoverflow')

    except requests.RequestException:
        cprint("[bold red]Error:[/] [default]No internet connection![/]")

    else:
        posts: dict = {
            item.get('title'): item.get('link')
            for item in response.json().get(['items'])
            if item.get('is_answered')
        }

        search_box = Panel(
            Group(
                '\n'.join([f'[bold]{title}[/]\n[underline color(33)]{link}[/]\n'
                for title, link in posts.items()])
            )
        , title=f'[bold]Search Result[/]', title_align='center',
        padding=(1, 1, 0, 1), style='color(29)')

        cprint(search_box)


def get_output(python_interpreter: str, output_file: Path) -> None:
    with open(output_file, "w+") as output_file_:
        subprocess.call([python_interpreter, output_file.__str__()], stdout=output_file_)


def interpret(python_interpreter: str, mirror_file: Path, args: list) -> None:
    subprocess.run([python_interpreter, mirror_file.__str__(), *args])


def display_error_message(exc_type: type, exc_message: Exception, traceback_: TracebackType) -> None:
    recipe: list = read_recipe(recipe_file=Path('recipe.pymgrcp'))

    template: list = [
        list_() for func in recipe
        for list_ in func(
            exc_type=exc_type,
            exc_message=exc_message,
            traceback_=traceback_
        )
    ]

    cprint(Panel(Group(*template), title='Exception', style='red', padding=(0, 1, 0, 1), highlight=False))


def prioritizing_options(options: dict) -> list[Callable]:

    prioritized_options, draft_options, available_options, second_level_options = [], [], [
        option for option, value in options.items() if value
    ], {
        'type': gen_type,
        'message': gen_message,
        'file': gen_file,
        'scope': gen_scope,
        'line': gen_line,
        'code': gen_code,
        'locals': gen_locals,
        'search': gen_search
    }

    for option in available_options:
        if option == 'trace' and 'locals' in available_options:
            if gen_trace in prioritized_options:
                prioritized_options.remove(gen_trace)

            prioritized_options.append(gen_trace_with_locals)

        elif option == 'inner' and 'locals' in available_options:
            if gen_inner in prioritized_options:
                prioritized_options.remove(gen_inner)

            prioritized_options.append(gen_inner_with_locals)

        elif option == 'trace':
            if gen_trace_with_locals not in prioritized_options:
                prioritized_options.append(gen_trace)

        elif option == 'inner':
            if gen_inner_with_locals not in prioritized_options:
                prioritized_options.append(gen_inner)

        else:
            draft_options.append(second_level_options.get(option))

    if not prioritized_options:
        prioritized_options.extend(draft_options)


    return prioritized_options


def gen_mirror_header() -> list[str]:
    header: list = [
        'import sys\n',
        'from pymg import display_error_message\n',
        'sys.excepthook = display_error_message\n'
    ]

    return header


def get_version() -> str:
    return '2.0.0'


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument('python_file', required=False, nargs=-1)
@click.option('-x', '--syntax', is_flag=True, help="The health of the file will be evaluated in terms of Python syntax rules. If there are no problems, the statement INTACT will be displayed, otherwise the syntax problem will be tracked and then displayed.")
@click.option('-t', '--type', is_flag=True, help="The type of exception that occurred will be displayed. In all options (exc: -L, -C, -F), exception type and message are displayed. However, this option can be used to display the exception type alone.")
@click.option('-m', '--message', is_flag=True, help="The exception message generated by the interpreter will be displayed. Just like the --type option, this option is used to display the exception message only. Otherwise, the exception message will be displayed anyway (exc: in -L, -C, -F options).")
@click.option('-f', '--file', is_flag=True, help="The full path of the python file that was interpreted and has an error will be displayed. This option, like the --line option, has conditions to be combined.")
@click.option('-s', '--scope', is_flag=True, help="")
@click.option('-l', '--line', is_flag=True, help="The line number that caused the exception will be displayed. This option can be combined with all options except --syntax, --trace, --inner and --search.")
@click.option('-c', '--code', is_flag=True, help="The code that caused the exception will be displayed. This option, like the --line option, has conditions to be combined.")
@click.option('-T', '--trace', is_flag=True, help="All paths that contributed to the creation of the exception will be tracked, and then, with separation, each created stack will be displayed.")
@click.option('-i', '--inner', is_flag=True, help="Like the --trace option, the entire path that contributed to the exception will be traced, with the difference that only the internal stacks related to the interpreted file will be displayed.")
@click.option('-L', '--locals', is_flag=True, help="")
@click.option('-S', '--search', is_flag=True, help="According to the exception that occurred and the generated message, with the help of stackoverflow's free api, the search to find a solution will be started. and finally the result will be displayed in the form of links that refer to stackoverflow and users solutions.")
@click.option('-o', '--output', nargs=1, help="")
@click.option('-r', '--recent', is_flag=True, help="")
@click.option('-v', '--version', is_flag=True, help='pymg version will be displayed. For more information and access to the latest changes, visit the pymg GitHub repository at https://github.com/mimseyedi/pymg.')
def main(**options):
    """
    pymg is a CLI tool that can interpret Python files and display errors in a more readable form.\n
    This tool interprets the selected Python file using the Python interpreter that is already installed on the system, and in case of errors, it displays the errors in separate, diverse and more readable forms.\n
    more information: https://github.com/mimseyedi/pymg
    """

    pass


if __name__ == '__main__':
    main()
