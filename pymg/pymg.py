"""
  _ __  _   _ _ __ ___   __ _
 | '_ \| | | | '_ ` _ \ / _` |
 | |_) | |_| | | | | | | (_| |
 | .__/ \__, |_| |_| |_|\__, |
 | |     __/ |           __/ |
 |_|    |___/           |___/

pymg is a CLI tool that can interpret Python files and
display errors in a more optimized and readable way.

This tool interprets the selected Python file using the Python interpreter
that is already installed on the system, and in case of errors, it displays
the errors in separate, diverse and more readable forms.

pymg Github repository: https://github.com/mimseyedi/pymg
"""


import os
import sys
import json
import click
import subprocess
from pathlib import Path


VERSION: str = '1.0.0'
HEADER_FILE: Path = Path(Path(__file__).parent, 'template', 'HEADER.json')
FOOTER_FILE: Path = Path(Path(__file__).parent, 'template', 'FOOTER.json')
ANALYSIS_FILE: Path = Path(Path(__file__).parent, 'out.py')
CONTEXT_SETTINGS: dict = {'help_option_names': ['-h', '--help']}


def read_json(json_path: Path) -> dict:
    """
    The task of this function is to read a json file.
    This function is written to read header and footer files.

    :param json_path: A json file with .json suffix.
    :return: dict
    """

    return json.loads(json_path.read_text(encoding='utf-8'))


def generate_header(header_file: Path) -> list[str]:
    """
    The task of this function is to generate the analysis file header.

    :param header_file: The path to the json file that contains the header information.
    :return: list[str]
    """

    header: list = read_json(json_path=header_file)["header"]

    return header


def generate_footer(footer_file: Path, modes: list[str], source_file: Path) -> list[str]:
    """
    The task of this function is to generate the analysis file footer in different mode.

    :param footer_file: The path to the json file that contains the footer information.

    :param modes: Different modes of making footer:
    ['standard', 'type', 'message', 'line', 'code', 'file',
    trace', 'inner', 'search', 'justline', 'justcode', 'justfile']

    :param source_file: The path of the file selected by the user for interpretation.

    :return: list[str]
    """

    footer_info: dict = read_json(json_path=footer_file)

    footer, all_modes = footer_info['static'], footer_info['modes']

    footer[3] = f"    FILE = '{Path(os.getcwd(), source_file).__str__()}'\n"

    if 'standard' in modes:
        footer.extend(all_modes['standard'])

    elif 'trace' in modes:
        footer.extend(all_modes['trace'])

    elif 'inner' in modes:
        footer.extend(all_modes['inner'])

    elif 'search' in modes:
        footer.extend(all_modes['search'])

    else:
        if 'type' in modes or 'message' in modes or \
                'justline' in modes or 'justcode' in modes or 'justfile' in modes:
            for _ in range(2):
                footer.pop()

        if 'type' in modes and 'message' in modes:
            footer.append(all_modes['type'])
            footer.append(all_modes['message'])

            modes.remove('type')
            modes.remove('message')

        else:
            if 'type' in modes:
                footer.append(all_modes['type'])
                modes.remove('type')

            elif 'message' in modes:
                footer.append(all_modes['message'])
                modes.remove('message')

        for index in range(len(modes)):
            if modes[index] in ['justline', 'justcode', 'justfile']:
                modes[index] = modes[index][4:]

        for mode in modes:
            footer.append(all_modes[mode])

            if mode == 'code':
                footer.append("    print(stack_trace[3])\n")

    footer.append("    print()")

    return footer


def read_source(path: Path) -> bool|list[str]:
    """
    The task of this function is to read the source:
    (The path of the file selected by the user for interpretation).

    :param path: The path of the file selected by the user for interpretation.
    :return: bool|list[str]
    """

    try:
        if path.__str__().endswith('.py'):
            with open(path, 'r') as source_file:
                source: list = source_file.readlines()

            return source

        return False

    except FileNotFoundError:
        return False

    except IsADirectoryError:
        return False


def remove_analysis_file(path: Path) -> None:
    """
    The task of this function is to remove an analysis file.
    This is done so that the new analysis file is replaced correctly.

    :param path: The path of the analysis file (A file created by the program to check errors).
    :return: None
    """

    os.remove(path=path.__str__())


def create_analysis_file(header: list[str], source: list[str], footer: list[str], out: Path) -> None:
    """
    The task of this function is to create an analysis file:
    (A file created by the program to check errors).

    :param header: A list containing analysis file header information.
    :param source: The path of the file selected by the user for interpretation.
    :param footer: A list containing analysis file footer information.
    :param out: The path of the analysis file (A file created by the program to check errors).
    :return: None
    """

    source: list = list(map(lambda x: "    " + x, source))

    analysis_text: list = [*header, *source, *footer]

    if out.exists():
        remove_analysis_file(path=out)

    with open(out, "w+") as analysis_file:
        analysis_file.write(''.join(analysis_text))


def get_syntax(analysis_file: Path) -> tuple[bool, str]:
    """
    The task of this function is to catch the syntax problems of the file containing the code.

    :param analysis_file: The path of the analysis file (A file created by the program to check errors).
    :return: tuple[bool, str]
    """

    syntax: subprocess.CompletedProcess = subprocess.run([sys.executable, '-m', 'py_compile',
                                                          analysis_file],
                                                          capture_output=True)

    if len(syntax.stderr.decode()) > 0:
        for index, char in enumerate(syntax.stderr.decode()):
            if char == ',':
                pymg_msg = syntax.stderr.decode()[index + 2:]
                break

        message: list = pymg_msg.split("\n")

        line_number: str = str(int(message[0].split()[-1]) - 4)

        message[0] = message[0].split()[0].capitalize() + ": " + line_number
        message[1] = "Code: " + message[1].strip()
        message[2] = " " * 2 + "\033[31m" + message[2] + "\033[0m"

        exception_message: str = message[3]

        for _ in range(2):
            message.pop()

        message.insert(0, "\nException type: SyntaxError")
        message.insert(1, f"Exception message: {exception_message}")

        return False, '\n'.join(message)

    return True, 'intact.'


def check_syntax(source_file: Path) -> None:
    """
    The task of this function is to check and display the syntax problems of the file containing the code.

    :param source_file: The path of the file selected by the user for interpretation.
    :return: None
    """

    header: list = generate_header(header_file=HEADER_FILE)
    footer: list = generate_footer(footer_file=FOOTER_FILE,
                                   modes=['standard'], source_file=source_file)
    source: list = read_source(path=source_file)

    create_analysis_file(header=header,
                         source=source,
                         footer=footer,
                         out=Path(Path(__file__).parent, 'out.py'))

    response, message = get_syntax(Path(Path(__file__).parent, 'out.py'))

    click.echo(message.upper() if response else message)


def analyze(source_file: Path, args: list, modes: list) -> None:
    """
    The task of this function is to check and analyze the analysis file.
    If there is no problem, the file will be interpreted correctly, and
    if there is an error, the error will be displayed.

    :param source_file: The path of the file selected by the user for interpretation.
    :param args: Command line arguments that are passed to the program.
    :param modes: Type of analysis request.
    ['standard', 'type', 'message', 'line', 'code', 'file', trace']

    :return: None
    """

    header: list = generate_header(header_file=HEADER_FILE)
    footer: list = generate_footer(footer_file=FOOTER_FILE,
                                   modes=modes, source_file=source_file)
    source: list = read_source(path=source_file)

    create_analysis_file(header=header,
                         source=source,
                         footer=footer,
                         out=Path(Path(__file__).parent, 'out.py'))

    response, message = get_syntax(analysis_file=Path(Path(__file__).parent, 'out.py'))

    if not response:
        click.echo(message)
    else:
        if len(args) == 0:
            subprocess.run([sys.executable,
                            Path(Path(__file__).parent, 'out.py').__str__()])

        else:
            subprocess.run([sys.executable,
                            Path(Path(__file__).parent, 'out.py').__str__(), *args])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('python_file', required=False, nargs=-1)
@click.option('-x', '--syntax', is_flag=True, help="The health of the file will be evaluated in terms of Python syntax rules. If there are no problems, the statement INTACT will be displayed, otherwise the syntax problem will be tracked and then displayed.")
@click.option('-t', '--type', is_flag=True, help="The type of exception that occurred will be displayed. In all options (exc: -L, -C, -F), exception type and message are displayed. However, this option can be used to display the exception type alone.")
@click.option('-m', '--message', is_flag=True, help="The exception message generated by the interpreter will be displayed. Just like the --type option, this option is used to display the exception message only. Otherwise, the exception message will be displayed anyway (exc: in -L, -C, -F options).")
@click.option('-l', '--line', is_flag=True, help="The line number that caused the exception will be displayed. This option can be combined with all options except --syntax, --trace, --inner and --search.")
@click.option('-jl', '--justline', is_flag=True, help="The line number that caused the exception will be displayed alone. like the --line option, has conditions to be combined.")
@click.option('-c', '--code', is_flag=True, help="The code that caused the exception will be displayed. This option, like the --line option, has conditions to be combined.")
@click.option('-jc', '--justcode', is_flag=True, help="The code that caused the exception will be displayed alone. This option, like the --line option, has conditions to be combined.")
@click.option('-f', '--file', is_flag=True, help="The full path of the python file that was interpreted and has an error will be displayed. This option, like the --line option, has conditions to be combined.")
@click.option('-jf', '--justfile', is_flag=True, help="The full path of the python file that was interpreted and has an error will be displayed alone. This option, like the --line option, has conditions to be combined.")
@click.option('-T', '--trace', is_flag=True, help="All paths that contributed to the creation of the exception will be tracked, and then, with separation, each created stack will be displayed.")
@click.option('-i', '--inner', is_flag=True, help="Like the --trace option, the entire path that contributed to the exception will be traced, with the difference that only the internal stacks related to the interpreted file will be displayed.")
@click.option('-s', '--search', is_flag=True, help="According to the exception that occurred and the generated message, with the help of stackoverflow's free api, the search to find a solution will be started. and finally the result will be displayed in the form of links that refer to stackoverflow and users solutions.")
@click.option('-v', '--version', is_flag=True, help='pymg version will be displayed. For more information and access to the latest changes, visit the pymg GitHub repository at https://github.com/mimseyedi/pymg.')
def main(**kwargs):
    """
    pymg is a CLI tool that can interpret Python files and display errors in a more optimized and readable way.\n
    This tool interprets the selected Python file using the Python interpreter that is already installed on the system, and in case of errors, it displays the errors in separate, diverse and more readable forms.\n
    more information: https://github.com/mimseyedi/pymg
    """

    if kwargs['version'] and len(kwargs['python_file']) == 0:
        click.echo(VERSION)

    else:
        if len(kwargs['python_file']) == 0:
            click.echo(
                "Usage: pymg [OPTIONS] [PYTHON_FILE]...\nTry 'pymg --help' for help.\n\nError: Missing argument 'PYTHON_FILE...'.")

        else:
            if kwargs['python_file'][0].endswith('.py'):
                if Path(kwargs['python_file'][0]).exists():

                    if kwargs['syntax']:
                        check_syntax(kwargs['python_file'][0])

                    else:
                        if all(val == False for val in kwargs.values() if isinstance(val, bool)):
                            analyze(source_file=kwargs['python_file'][0],
                                    args=kwargs['python_file'][1:],
                                    modes=['standard'])
                        else:
                            options: list = [key for key, value in kwargs.items()
                                             if value and key not in ['python_file', 'version']]

                            if len(options) > 0 and kwargs['version'] is False:
                                analyze(source_file=kwargs['python_file'][0],
                                        args=kwargs['python_file'][1:],
                                        modes=options)
                            else:
                                click.echo(
                                    f"Usage: pymg [OPTIONS] [PYTHON_FILE]...\nTry 'pymg --help' for help.\n\nError: No such option for this part: -v, --version")
                else:
                    click.echo(f"Error: File '{kwargs['python_file'][0]}' does not exist.")
            else:
                click.echo(f"Error: The '{kwargs['python_file'][0]}' file must be a Python file.")


if __name__ == '__main__':
    main()
