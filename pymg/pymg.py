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


def read_json(json_path: Path) -> dict:
    """
    The task of this function is to read a json file.
    This function is written to read header and footer files.

    :param json_path: A json file with .json suffix.
    :return: dict
    """

    return json.loads(json_path.read_text(encoding='utf-8'))


def generate_header(source_file: Path) -> list[str]:
    """
    The task of this function is to generate the analysis file header.

    :return: source_file: The path of the file selected by the user for interpretation.
    :return: list[str]
    """

    header: list = read_json(Path(Path(__file__).parent, 'template', 'HEADER.json'))["header"]

    header[2] = f"FILE = '{Path(os.getcwd(), source_file).__str__()}'\n"

    return header


def generate_footer(modes: list[str]) -> list[str]:
    """
    The task of this function is to generate the analysis file footer in different mode.

    :param modes: Different modes of making footer:
    ['standard', 'type', 'message', 'line', 'code', 'file', trace']

    :return: list[str]
    """

    footer: list = read_json(Path(Path(__file__).parent, 'template', 'FOOTER.json'))['static']

    all_modes: dict = read_json(Path(Path(__file__).parent, 'template', 'FOOTER.json'))['modes']

    if 'standard' in modes:
        footer.append(all_modes['standard'])

    elif 'trace' in modes:
        footer.extend(all_modes['trace'])

    else:
        if 'type' in modes or 'message' in modes:
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

    pass


def check_syntax(source_file: Path) -> None:
    """
    The task of this function is to check and display the syntax problems of the file containing the code.

    :param source_file: The path of the file selected by the user for interpretation.
    :return: None
    """

    pass


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

    pass


@click.command()
@click.argument('python_file', required=False, nargs=-1)
@click.option('-v', '--version', is_flag=True, help='Display Version of pymg.')
@click.option('-x', '--syntax', is_flag=True, help='Display file syntax status.')
@click.option('-t', '--type', is_flag=True, help='Display the type of exception.')
@click.option('-m', '--message', is_flag=True, help='Display the exception message.')
@click.option('-l', '--line', is_flag=True, help='Display the line number that caused the error.')
@click.option('-c', '--code', is_flag=True, help='Display the code that caused the error.')
@click.option('-f', '--file', is_flag=True, help='Display the full path of the file that has an error.')
@click.option('-T', '--trace', is_flag=True, help='Display all tracked stacks of errors.')
def main(**kwargs):
    """
    pymg is a CLI tool that can interpret Python files and display errors in a more optimized and readable way.\n
    This tool interprets the selected Python file using the Python interpreter that is already installed on the system, and in case of errors, it displays the errors in separate, diverse and more readable forms.\n
    more information: https://github.com/mimseyedi/pymg
    """

    pass


if __name__ == '__main__':
    main()
